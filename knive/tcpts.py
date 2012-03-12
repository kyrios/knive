#
# tcpts.py
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

from foundation import KNOutlet, KNInlet

from twisted.internet.protocol      import ReconnectingClientFactory, ServerFactory
from twisted.protocols              import basic
from twisted.application            import internet
from zope.interface                 import implements
from twisted.python                 import log
from twisted.internet               import reactor
from twisted.internet.interfaces    import ILoggingContext
from twisted.internet.defer         import Deferred 

import hashlib
import random

class TCPTSClientFactory(ReconnectingClientFactory):
    """docstring for TCPTransportFactory"""
    
    initialDelay = .1
    secret = None
    maxDelay = 8

    def clientConnectionFailed(self, connector, reason):
        log.err('connection failed: %s' % reason)
        if self.continueTrying:
            self.connector = connector
            self.retry()
    
    def clientConnectionLost(self, connector, reason):
        log.err('connection lost: %s' % reason)
        self.protocol.connectionEstablished = False
        if self.continueTrying:
            self.connector = connector
            self.retry()
            
    def buildProtocol(self, addr):
        log.msg("TCPTSClient connected to %s" % addr)
        self.protocol = TCPTSClientProtocol()
        self.protocol.factory = self
        return self.protocol

    def sendData(self,data):
        if self.protocol.connectionEstablished:
            self.protocol.sendData(data)
                
        
class TCPTSClient(KNOutlet):
    """Connect to a simple TCP Server accepting Mpeg-TS Data after a simple handshake auth"""
    implements(ILoggingContext)
    
    
    def __init__(self, hostname,port,secret='12345'):
        super(TCPTSClient,self).__init__(name="%s:%s" % (hostname,port))
        self.hostname = hostname
        self.port = port
        self.factory = TCPTSClientFactory()        
        self.factory.service = self
        self.factory.secret = secret
        self.connection = internet.TCPClient(self.hostname, self.port, self.factory)
        
    def logPrefix(self):
        """docstring for logPrefix"""
        return 'TCPTSClient'
    
    def _start(self):
        """docstring for startService"""
        self.connection.startService()
        defer = Deferred()
        
        def _checkRunning():
            if not self.factory:
                self.log.debug('Factory not ready')
            if not self.factory.protocol:
                self.log.debug('Protocol not ready')
            else:
                if self.factory.protocol.state == 99:
                    self.log.info('Connection established')
                    defer.callback(self)
                    return
                else:
                    self.log.debug('Unknown protocol state %s' % self.factory.protocol.state)
            self.log.info("Waiting for connecion to %s:%s" % (self.hostname,self.port))
            reactor.callLater(1,_checkRunning)
                
        _checkRunning()
        return defer
                
    def dataReceived(self,data):
        """docstring for dataReceived"""
        self.factory.sendData(data)
        
    def connectionFailed(self):
        """docstring for connectionFailed"""
        reactor.stop()
        
    def __str__(self):
        """docstring for __str__"""
        return "%s ->%s:%s" % (self.__class__.__name__,self.hostname,self.port)

class TCPTSClientProtocol(basic.LineReceiver):
    """docstring for TCPTSClientProtocol"""
    challenge = None
    connectionEstablished = False
    
    def connectionMade(self):
        self.state = 0
        self.challenge = None
        self.connectionEstablished = True
        log.msg("Connected TCPTSClientProto")

    def sendData(self,data):
        """Sending of payload data after the connection is established and handshake is ready"""
        if self.state == 99:
            self.transport.write(data)
    
    def lineReceived(self,line):
        """docstring for lineReceived"""
        #log.msg("Received %s" % line)
        if self.state == 0:
            if line == 'TCPTS 0.1':
                self.state = 1
                log.msg("Connected to TCPTSServer")
            else:
                self.protocolMissmatch()
        elif self.state == 1:
            log.msg("Secret: %s" % self.factory.secret)
            log.msg("Sending challenge reply: %s - %s - %s" % (line,self.factory.secret,hashlib.sha224(line + self.factory.secret).hexdigest()))
            self.sendLine(hashlib.sha224(line + self.factory.secret).hexdigest())
            self.state = 2
        elif self.state == 2:
            if line == 'Authenticated':
                log.msg("Autenticated")
                self.state = 99
            else:
                log.err("Authentication not succesfull. Check secret on client/server")
                reactor.stop()
        else:
            log.err("Unknown data received from server")
            self.transport.loseConnection()
    
    def protocolMissmatch(self):
        """docstring for protocolMissmatch"""
        log.err("Protocol missmatch")
        self.transport.loseConnection()


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

class TCPTSServer(KNInlet):
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

    def outletStarted(self,outlet):
        """Stuff to be done after all outlets have started but before the inlet is notified"""
        self.log.info("Starting")

    def _start(self):
        self.connection.startService()

    def _willStop(self):
        """Stuff to be done before outlets get the stop command"""
        self.connection.stopService()

    def dataReceived(self,data):
        """The protocol writes data to this method. Overwrite it and do something meaningfull with it"""
        self.sendDataToAllOutlets(data)

class TCPTSServerFactory(ServerFactory):
    """docstring for TCPTSServerFactory"""
    protocol = TCPTSServerProtocol
    
    def __init__(self,secret):
        """docstring for __init__"""
        self.secret = secret
        log.msg("%s running with secret: %s" % (self,self.secret))

