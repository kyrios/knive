from foundation import KNDistributor

from twisted.internet.protocol      import ReconnectingClientFactory, ClientFactory, Protocol, ServerFactory
from twisted.protocols              import basic
from twisted.application            import service, internet
from zope.interface                 import implements
from twisted.python                 import log
from twisted.internet               import reactor, defer
from twisted.internet.interfaces    import ILoggingContext

import hashlib
import random
import datetime
import logging


class TCPTSServerProtocol(basic.LineReceiver):
    """docstring for TCPTSServerProtocol"""
    state = 0
    challenge = None        
    
    def connectionMade(self):
        self.state = 0
        self.challenge = None
        self.sendLine('TCPTS 0.1')
        self.sendLine(self.createChallenge())
        self.state = 1

    def createChallenge(self):
        """docstring for createChallenge"""
        self.challenge = hashlib.sha224(str(random.random())).hexdigest()
        log.msg("Challenge sent: %s" % self.challenge)
        return self.challenge
        
    def challengeAccepted(self,check):
        """docstring for checkAuth"""
        log.msg("Received %s from client. Checking with secret %s (%s)" % (check,self.factory.secret,hashlib.sha224(self.challenge + self.factory.secret).hexdigest()))
        return check == hashlib.sha224(self.challenge + self.factory.secret).hexdigest()
        
    def lineReceived(self,line):
        """docstring for lineReceived"""
        if self.state == 1:
            if self.challengeAccepted(line):
                self.state = 2
                log.msg("Handshake okay")
                self.sendLine('Authenticated')
                self.state = 99
                self.setRawMode()
            else:
                log.err("Handshake not sucesfull. Check the secret(s) on client and server. They have to match")
                self.sendLine('Wrong reply!')
                self.transport.loseConnection()
        else:
            log.err("Didn't expect data. Closing connection")
            self.transport.loseConnection()
            
    def rawDataReceived(self,data):
        """handle the mpeg-ts data"""
        self.factory.service.dataReceived(data)

class TCPTSServer(KNDistributor):
    """Create a simple TCP Server accepting Mpeg-TS Data after a handshake auth"""

    def __init__(self, name='Unknown',hostname="0.0.0.0",port=3333,secret='123467'):
        super(TCPTSServer, self).__init__(name=name)
        self.hostname = hostname
        self.port = port

        self.factory = TCPTSServerFactory(secret)
        self.factory.service = self
        self.connection = internet.TCPServer(self.port, self.factory)

    def connectionFailed(self):
        self.log.err('Connection failed. Can not continue.')
        reactor.stop()

    def didStart(self):
        """Stuff to be done after all outlets have started but before the inlet is notified"""
        self.connection.startService()

    def willStop(self):
        """Stuff to be done before outlets get the stop command"""
        self.connection.stopService()

class TCPTSServerFactory(ServerFactory):
    """docstring for TCPTSServerFactory"""
    protocol = TCPTSServerProtocol
    
    def __init__(self,secret):
        """docstring for __init__"""
        self.secret = secret
        log.msg("%s running with secret: %s" % (self,self.secret))
