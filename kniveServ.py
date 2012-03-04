#!/usr/bin/env python

import logging
import logging.handlers
import os

from knive.knive  import  makeKnive, KniveLogggingObserver
# from knive  import streaming
# from knive  import foundation
# from knive  import tcpts
# from knive  import files
# from knive  import httplive
# from knive  import base
# from knive  import mplayer

from webknive   import web


from twisted.internet           import reactor
from twisted.conch.manhole_tap  import makeService as makeManholeService



rootLogger = logging.getLogger('')
rootLogger.setLevel(logging.DEBUG)
observer = KniveLogggingObserver()

observer.start()

# Set up console output
console = logging.StreamHandler()
consoleFormat = logging.Formatter('%(name)s:%(message)s')
console.setFormatter(consoleFormat)
console.setLevel(logging.DEBUG)
rootLogger.addHandler(console)
knive = makeKnive(os.path.abspath('knive.conf'))


# Logfile output
logfile = logging.handlers.RotatingFileHandler(
                                                knive.config['logging']['logfile'], 
                                                mode='a', 
                                                maxBytes=knive.config['logging']['filesize']*1024, 
                                                backupCount=knive.config['logging']['keepfiles']
                                               )
logfileFormat = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
#logfile.setFormatter(logfileFormat)
if knive.config['logging']['loglevel'] == 'DEBUG':
    loglevel = logging.DEBUG
elif knive.config['logging']['loglevel'] == 'INFO':
    loglevel = logging.INFO
else:
    loglevel = logging.WARN
logfile.setLevel(loglevel)


rootLogger.addHandler(logfile)

logging.info("Knive starting..")

if knive.config['webservice']['enabled']:
    webservice = web.WebKnive(port=knive.config['webservice']['port'],backend=knive)
    webservice.setServiceParent(knive)

    # webLogging = logging.StreamHandler(webservice)
    # consoleFormat = logging.Formatter('%(message)s')
    # webLogging.setFormatter(consoleFormat)
    # webLogging.setLevel(logging.DEBUG)
    # rootLogger.addHandler(webLogging)

for channelSection in knive.config['channels']:
    channel = knive.createChannelFromConfig(knive.config['channels'][channelSection])


manholenamespace = {'knive': knive}
manholeOptions = {
    'namespace' : manholenamespace,
    'passwd' : 'users.txt',
    'sshPort': '4022',
    'telnetPort': None
}

manHoleService = makeManholeService(manholeOptions)
manHoleService.setServiceParent(knive)


knive.startService()
#show0.startStreaming()
# reactor.callLater(1,show0.startEpisode,episode)


reactor.callLater(10,reactor.stop)
reactor.run()
