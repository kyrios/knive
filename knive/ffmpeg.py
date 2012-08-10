#!/usr/bin/env python
#
# ffmpeg.py
# Copyright (c) 2012 Thorsten Philipp <kyrios@kyri0s.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in the 
# Software without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import re
from foundation import KNDistributor, KNProcessProtocol
from twisted.internet       import reactor
from twisted.python         import log


class FFMpeg(KNDistributor):
    def __init__(self,ffmpegbin='/usr/bin/ffmpeg',encoderArguments=None):
        """Start a ffmpeg process.
        ffmpegbin:          path to ffmpeg
        encoderArguments:   a dictionary of ffmpeg arguments. 
                            If the value of a item is None it 
                            is considered to have no value. (Example: -vn)"""
        super(FFMpeg,self).__init__(name='FFMpeg')
        self.protocol = FFMpegProtocol()
        self.protocol.factory = self
        self.ffmpegbin = ffmpegbin

        self.encoderArguments = dict(encoderArguments)
        del self.encoderArguments['codecstring']

        self._targetFPS = 25
        try:
            self._targetFPS = self.encoderArguments['r']
        except KeyError:
            pass
        
        self.fargs = ['ffmpeg','-y','-i','-']
        for key in self.encoderArguments.keys():
            if self.encoderArguments[key] is None:
                continue # No None values
            if type(self.encoderArguments[key]) == tuple or type(self.encoderArguments[key]) == list : #Some ffmpeg argument may apear more than once. (-vpre)
                for val in self.encoderArguments[key]:
                    self.fargs.append("-%s" % key)
                    self.fargs.append("%s" % val)
            else:
                self.fargs.append("-%s" % key)
                if self.encoderArguments[key] is True: #Some ffmpeg arguments are of boolean type. There or not. No value
                    pass
                else:
                    self.fargs.append("%s" % self.encoderArguments[key])
                
        self.fargs.append("-")
        self.log.debug("FFMpegcommand: %s %s" % (self.ffmpegbin," ".join(self.fargs)))
        self.cmdline = "%s %s" % (self.ffmpegbin," ".join(self.fargs))
        
    def _start(self):
        """Stuff to be done after all outlets have started but before the inlet is notified"""
        self.log.debug('Spawning new FFMpeg process')
        reactor.spawnProcess(self.protocol,self.ffmpegbin,self.fargs)

    def dataReceived(self,data):
        """Data received from our inlet. Pipe this data to the ffmpeg process"""
        if not self.running:
            raise(Exception("Process not running"))
        else:
            self.protocol.writeData(data)    


class FFMpegProtocol(KNProcessProtocol):
    """Parsing and communication with FFMpeg"""
    fps = 0
    # Output matching
    REversion = re.compile('FFmpeg version')
    #frame=97 fps= 21 q=30.0 size=     443kB time=2.32 bitrate=1564.3kbits/s dup=12 drop=0 
    #frame=   64 fps=0.0 q=32.0 size=      19kB time=00:00:00.84 bitrate= 186.2kbits/s dup=13 drop=47

    REencodingStats = re.compile('frame=\s*(\d+)\s*fps')
    REencodingStatsFPS = re.compile('fps=\s*(\d+\.?\d?)\s*q')
    #size=     560kB time=64.91 bitrate=  70.7kbits/s
    REencodingStatsAudio = re.compile('size= *(\d+)kB *time=\d+')
    
    
    def errReceived(self, data):
        lines = str(data).splitlines()
        # log.msg(data)
        for line in lines:
            self._lastlogline = line
            if(self.__class__.REversion.match(line)):
                log.msg(line)
            elif(self.__class__.REencodingStats.match(line)):
                self.stats = line
                self.updateStats(line)
            elif(self.__class__.REencodingStatsAudio.match(line)):
                self.stats = line
            else:
                self._lastlogline = line
                log.msg("%s" % (line))

    def updateStats(self,line):
        match = self.__class__.REencodingStatsFPS.search(line)
        self.currentFPS = float(match.group(1))
        #log.msg("Current FPS: %s Target FPS: %s " % (self.currentFPS,self.factory.targetFPS))
        if int(self.currentFPS) < int(self.factory._targetFPS):
            log.msg("WARNING! Current encoding FPS (%s) below target FPS (%s) Not encoding fast enough! Reduce encoding quality!" % (int(self.currentFPS),self.factory._targetFPS))
    
    def outReceived(self, data):
        """Received data from ffmpegs STDOUT"""
        self.factory.sendDataToAllOutlets(data)
