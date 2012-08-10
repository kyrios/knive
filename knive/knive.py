# knive.py
# Copyright (c) 2012 Thorsten Philipp <kyrios@kyri0s.de>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import logging
import os
import configobj
import sys

from validate   import Validator

from channel    import Channel
from tcpts      import TCPTSServer
from httplive   import HTTPLiveStream
from kninterfaces   import IKNInlet

from twisted.application        import service
from twisted.python.log         import *

# from twisted.application import service

class Knive(service.MultiService):
    """A single service to rule them all. Singleton object for startup and stop of services."""

    def timoStart(self):
        self.channels[0].startEpisode()
    
    def __init__(self, configFile):
        service.MultiService.__init__(self)
        self.configFile = configFile
        self.config = None
        self.log = logging.getLogger('Knive')
        self.loadConfig()
        self.channels = []
        
        # from twisted.conch import manhole_tap
        # manhole_tap.makeService({"telnetPort": None,
        #                  "sshPort": "tcp:22101",
        #                  "namespace": {"channels": self.channels},
        #                  "passwd": "passwd"}).setServiceParent(application)
        
        
        """List of available channels."""

    def printOutlets(self,object,t=2,r=1):
        if r>10:
            Exception("Maximum recursion depth")
            sys.exit(1)
        if IKNInlet.providedBy(object):
            for outlet in object.outlets:
                print "%sOutlet: %s" % ("  "*t,outlet)
                self.printOutlets(outlet,t+2,r=r+1)

    def startService(self):
        """Start the service"""
        self.log.debug('Starting channels')
        service.MultiService.startService(self)
        for channel in self.channels:
            self.log.info('Starting channel %s' % channel)
            self.printOutlets(channel)
            channel.start()

    def stopService(self):
        for channel in self.channels:
            channel.stop()
        service.MultiService.stopService()

    def createChannelFromConfig(self,configObject):
        print configObject
        channel = Channel(configObject['name'],self.config,configObject['slug'] )
        channel.url = configObject['url']

        
        # ================
        # = Inlet/Source =
        # ================

        if configObject['source']['type'] == 'kniveTCPSource':
            channel.inlet = TCPTSServer(
                                                secret=configObject['source']['sharedSecret'],
                                                port=configObject['source']['listenPort']
                                            )
        else:
            print "Unknown Inlet Type %s" % knive.config['stream']['inlet']
            sys.exit(1)

        # ===============
        # = Set outlets =
        # ===============
        for outletsectionname in configObject['outlets']:
            logging.debug('Setting up outlet: %s' % outletsectionname)
            outletConfig = configObject['outlets'][outletsectionname]
            if outletConfig['type'] == 'HTTPLive': 
                try:
                    httplivestream = HTTPLiveStream(channel=channel,destdir=self.config['paths']['knivedata'],segmentServer=outletConfig['segmentServer'])
                    channel.addOutlet(httplivestream)
                except Exception, err:
                    logging.exception(err)
                    sys.exit(1)

                for qualityname in outletConfig.sections:
                    qualityConfig = outletConfig[qualityname]
                    httplivestream.createQuality(qualityname,qualityConfig,ffmpegbin=self.config['paths']['ffmpegbin'])
                
                

            elif outletConfig['type'] == 'StreamArchiver':
                
                archiver = files.FileWriter(
                                                    knive.config[outletsectionname]['outputdir'],
                                                    suffix=knive.config[outletsectionname]['suffix'],
                                                    keepFiles=knive.config[outletsectionname]['keepfiles'],
                                                    filename=knive.config[outletsectionname]['filename']
                                                )
                channel.addOutlet(archiver)
            elif outletConfig['type'] == 'MEncoder':
                mplayer = mplayer.Player(binary=knive.config[outletsectionname]['mplayerbin'])
                channel.addOutlet(mplayer)
            else:
                self.log.error('Unknown outlet type %s' % outletsectionname)

        self.addChannel(channel)


        
    def createChannel(self,channelName):
        """Factory function for Channel Objects. Registers the channel.
        Returns: new Channel Object"""
        
        channel = Channel()
        channel.name = channelName
        self.addChannel(channel)
        return channel
        
    def addChannel(self,channel):
        """Register a Channel object"""
        if channel not in self.channels:
            self.channels.append(channel)
            if self.running:
                channel.start()

    def removeChannel(self,channel):
        if channel in self.channels:
            if self.running:
                channel.stop()
            self.channels.remove(channel)
        
    def loadConfig(self):
        """Load and validate the configuration File"""
        self.log.debug("Reading configuration from %s" % os.path.abspath(self.configFile))
        try:
            #print os.path.abspath('knive.conf.spec')
            self.config = configobj.ConfigObj(self.configFile,file_error=True,configspec=os.path.abspath(os.path.dirname(__file__) + os.path.sep + 'knive.conf.spec'))
        except (configobj.ConfigObjError, IOError), e:
            print 'Could not read "%s": %s' % (self.configFile, e)
            sys.exit(1)
        validator = Validator()
        results = self.config.validate(validator)

        if results != True:
            for (section_list, key, _) in configobj.flatten_errors(self.config, results):
                if key is not None:
                    print '%s in section "%s" does not conform to specification' % (key, ', '.join(section_list))
                else:
                    print 'The following section was missing:%s ' % ', '.join(section_list)
            sys.exit(1)
        
    def writeConfig(self):
        """Flush the current memory Config to disk"""
        pass


def makeKnive(configfile):
    return Knive(configfile)


class KniveLogggingObserver(PythonLoggingObserver):
    """docstring for KniveLogggingObserver"""
    
    def emit(self,eventDict):
        """docstring for emit"""
        if 'logLevel' in eventDict:
            level = eventDict['logLevel']
        elif eventDict['isError']:
            level = logging.ERROR
        else:
            level = logging.DEBUG
        text = textFromEventDict(eventDict)
        if text is None:
            return
        if eventDict['system'] != '-':
            logging.getLogger(eventDict['system']).log(level,text)
        else:
            self.logger.log(level, text)