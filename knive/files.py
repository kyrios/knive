#
# files.py
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

from twisted.internet       import fdesc, reactor
from zope.interface import implements
from twisted.application    import service
from twisted.python         import log
from foundation             import KNOutlet
import os
import shutil

import  foundation


class FileWriter(KNOutlet):
    """Write data received from self.inlet to file specified during init"""
    def __init__(self, outdir, filename = 'Unknown-knive-file',keepFiles=5, suffix=None):
        self.outfile = None
        if os.path.exists(outdir):
            self.outdir = outdir
        else:
            raise(Exception("Directory doesn't exist %s" % outdir))
        self.running = 0
        self.filename = filename
        self.keepFiles = keepFiles
        self.suffix = suffix
        self._outfileName = self.getFileName()
        
    def getFileName(self):
        """Return the filename this fileWriter will write as soon as the service starts"""
        if self.parent:
            self.filename = self.parent.getFileName()
        if self.suffix:
            self.filename = self.filename + self.suffix
        self._outfileName = self.outdir + os.path.sep + self.filename
        return self._outfileName
        
    def startService(self):
        """docstring for startService"""
        log.msg("Starting %s" % self)
        filename = self.getFileName()
        def checkAndMove(filename,offset=0):
            if os.path.isfile(self._outfileName) and offset <= self.keepFiles:
                offset += 1
                newFileName = self.outdir + os.path.sep + self.filename[:-(len(self.suffix))] + '.%s%s' % (offset,self.suffix)
                checkAndMove(newFileName,offset)
                if os.path.isfile(filename):
                    shutil.move(filename,newFileName)
                
        checkAndMove(self._outfileName)
        self.outfile = os.open(self._outfileName,os.O_WRONLY | os.O_NONBLOCK | os.O_CREAT)
        if not self.outfile:
            raise("Could not open %s" % self._outfileName)
        else:
            log.msg("Opened %s" % self._outfileName)
        fdesc.setNonBlocking(self.outfile)
        
        self.running = 1
        def syncToDisc():
            """docstring for flushToDisk"""
            
            os.fsync(self.outfile)
            if self.running:
                reactor.callLater(5,syncToDisc)
        syncToDisc()
        
    def stopService(self):
        """docstring for stopService"""
        self.running = 0
        os.close(self.outfile)
        
    def dataReceived(self,data):
        """docstring for writeData"""
        fdesc.writeToFD(self.outfile,data)
    
    def writeData(self,data):
        """docstring for writeData"""
        fdesc.writeToFD(self.outfile,data)
        
    def setParent(self,parent):
        """docstring for setParent"""
        self.parent = parent

      
    def __str__(self):
        """docstring for __str__"""
        try:
            return "%s (%s)" % (self.__class__.__name__,self._outfileName)
        except:
            return "%s" % (self.__class__.__name__) 