import logging
import os
import configobj
import sys

from validate   import Validator

from channel    import Channel
from tcpts      import TCPTSServer
from httplive   import HTTPLiveStream

from twisted.application        import service
from twisted.python.log         import *


class Knive(service.MultiService):
    """A single service to rule them all. Singleton object for startup and stop of services."""
    
    def __init__(self, configFile):
        service.MultiService.__init__(self)
        self.configFile = configFile
        self.config = None
        self.log = logging.getLogger('Knive')
        self.loadConfig()
        
        self.channels = []
        """List of available channels."""

    def startService(self):
        """Start the service"""
        service.MultiService.startService()
        for channel in self.channels:
            channel.start()

    def stopService(self):
        for channel in self.channels:
            channel.stop()
        service.MultiService.stopService()

    def createChannelFromConfig(self,configObject):
            channel = Channel(configObject['name'])
            channel.slug = configObject['slug']            
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
                        httplivestream = HTTPLiveStream(channel=channel,destdir=outletConfig['outputLocation'],publishURL=outletConfig['publishURL'])
                    except Exception, err:
                        logging.exception(err)
                        sys.exit(1)

                    sys.exit(1)
                    for quality in knive.config[outletsectionname]:
                        if isinstance(knive.config[outletsectionname][quality],configobj.Section):
                            httplivestream.addQuality(name=quality,config=knive.config[outletsectionname][quality])

                    #show0.addOutlet(httplivestream)

                elif outletConfig['type'] == 'StreamArchiver':
                    
                    archiver = files.FileWriter(
                                                        knive.config[outletsectionname]['outputdir'],
                                                        suffix=knive.config[outletsectionname]['suffix'],
                                                        keepFiles=knive.config[outletsectionname]['keepfiles'],
                                                        filename=knive.config[outletsectionname]['filename']
                                                    )
                    show0.addOutlet(archiver)
                elif outletConfig['type'] == 'MEncoder':
                    mplayer = mplayer.Player(binary=knive.config[outletsectionname]['mplayerbin'])
                    show0.addOutlet(mplayer)
                else:
                    self.log.error('Unknown outlet type %s' % outletsectionname)

        
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
            self.config = configobj.ConfigObj(self.configFile,file_error=True,configspec=os.path.abspath('knive/knive.conf.spec'))
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