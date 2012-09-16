#!/usr/bin/env python
#
# kniveServ.py
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
knive = makeKnive(os.path.abspath(os.path.dirname(__file__) + os.path.sep + 'knive.conf'))


# Logfile output
logfile = logging.handlers.RotatingFileHandler(
                                                knive.config['logging']['logfile'],
                                                mode='a',
                                                maxBytes=knive.config['logging']['filesize'] * 1024,
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

for channelSection in knive.config['channels']:
    channel = knive.createChannelFromConfig(knive.config['channels'][channelSection])


if knive.config['manhole']['enabled']:
    manholenamespace = {'knive': knive}
    manholeOptions = {
        'namespace': manholenamespace,
        'passwd': 'users.txt',
        'sshPort': knive.config['manhole']['port'],
        'telnetPort': None
    }

    manHoleService = makeManholeService(manholeOptions)
    manHoleService.setServiceParent(knive)

if knive.config['webservice']['enabled']:
    webservice = web.WebKnive(port=knive.config['webservice']['port'], backend=knive, resourcepath=knive.config['webservice']['resourcepath'])
    webservice.setServiceParent(knive)

    # webLogging = logging.StreamHandler(webservice)
    # consoleFormat = logging.Formatter('%(message)s')
    # webLogging.setFormatter(consoleFormat)
    # webLogging.setLevel(logging.DEBUG)
    # rootLogger.addHandler(webLogging)

knive.startService()
#show0.startStreaming()
# reactor.callLater(1,show0.startEpisode,episode)


# reactor.callLater(10,reactor.stop)
reactor.run()
