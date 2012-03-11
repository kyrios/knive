#
# foundation.py
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
"""Base Classes in KN projects

.. moduleauthor:: Thorsten Philipp <kyrios@kyri0s.de>

"""

from kninterfaces           import IKNStreamObject, IKNOutlet, IKNInlet
from zope.interface         import implements
from twisted.internet.defer import Deferred, maybeDeferred
from exceptions             import ServiceRunningWithoutOutlets, ServiceRunningWithouInlet
from twisted.internet       import protocol, reactor

import logging


class KNStreamObject(object):
    """KNStreamObject is a superclass for all classes that produce or consume data.
    The class handles basic starting and stopping of objects in the stream of data
    as well as logging and other basic stuff."""
    implements(IKNStreamObject)

    def __init__(self,name=None):
        super(KNStreamObject, self).__init__()
        self.running = False
        self.name = name
        self.log = logging.getLogger('[%s] %s' % (self.__class__.__name__,self.name))

    def start(self):
        self._start()
        self._didStart()
        self.running = True

    def stop(self):
        self.running = False

    def __str__(self):
        if self.name:
            return "<%s | %s>" % (self.name,self.__class__.__name__)
        else:
            return self.__instance__


class KNInlet(KNStreamObject):
    """Implementation of :class:`IKNInlet`"""
    implements(IKNInlet)
    def __init__(self, name=None):
        super(KNInlet, self).__init__(name=name)
        self.name = name
        self.outlets = []


    def start(self):
        """Start the module and all outlets. Notify the inlet when everything is running. Do not override this."""
        self.runningOutlets = 0

        defStarted = Deferred()

        self.log.debug('Starting. Outlets are: %s' % self.outlets)
        if not len(self.outlets):
            raise(ServiceRunningWithoutOutlets)

        if not self.running:

            self._willStart()

            # Start the outlets
            def _outletStarted(object):
                self.runningOutlets += 1
                if self.runningOutlets >= len(self.outlets):
                    #All outlets started
                    _allOutletsStarted()

            def _allOutletsStarted():
                self.running = True
                self._start()
                self.log.debug("Did start")
                defStarted.callback(self)

            for outlet in self.outlets:
                if not outlet.running:
                    self.log.debug('Starting outlet %s' % outlet)
                    d = maybeDeferred(outlet.start)
                    d.addCallback(_outletStarted)
                else:
                    _outletStarted(outlet)
            if not len(self.outlets):
                _allOutletsStarted()
        else:
            self.log.warning("%s is already running. Can not start" % self)
            d.errback('%s is already running. Can not start' % self)

        return defStarted

    def _willStart(self):
        """Stuff to be done before outlets gets the start command (implemented for IKNInlet)"""
        pass

    def _start(self):
        """Stuff to be done after all outlets have started but before the inlet is notified (IKNInlet)"""
        pass

    def _didStartAndNotifiedInlet(self):
        """Stuff to be done after all outlets have started and the inlet was notified (INKNInlet)"""
        pass

    def outletStarted(self,outlet):
        """called by our outlets after they started (IKNInlet)"""
        pass

    def _startFailed(self,outlet):
        pass

    def addOutlet(self,outlet):
        """Outlets receive data from the service when the service is running. Outlets need to be of type IKNOutlet.
        If not already done this service will be set as inlet on the specified outlet."""
        #
        self.log.debug('Adding outlet %s to %s' % (outlet,self))
        # print "Self.outlets:%s (%s)" % (self.outlets,id(self.outlets))
        # print "Outlet.outlets: %s (%s)" % (outlet.outlets,id(outlet.outlets))
        # return()
        if IKNOutlet.providedBy(outlet):
            if outlet.inlet != self:
                outlet.setInlet(self,recursiveCall=False)
            if outlet not in self.outlets:
                if outlet is not self:
                    self.outlets.append(outlet)
                    # print "Self.outlets:%s" % self.outlets
                    # print "Outlet.outlets: %s" % outlet.outlets
                else:
                    raise(Exception("Can't be an outlet of myself"))                    

        else:
            raise(Exception('%s does not implement %s' % (outlet,IKNOutlet)))

    def removeOutlet(self,outlet):
        """Remove the outlet from the list of outlets. The outlet will no longer receive any data."""
        if outlet in self.outlets:
            self.outlets.remove(outlet)
            outlet.inlet = None
            if outlet.running:
                raise(ServiceRunningWithouInlet)
        
    def getStats():
        """Return a string with statistics about data flow (bits p second?)"""
        pass
        

class KNOutlet(KNStreamObject):
    """Implementation of :class:`IKNOutlet`"""
    implements(IKNOutlet)
    def __init__(self, name=None):
        super(KNOutlet, self).__init__(name=name)
        self.name = name
        self.inlet = None

    def setInlet(self,inlet,recursiveCall=True):
        """Set the inlet of this service. This can only be changed when the service is stopped. The inlet is the datasource or input.
        If not already done this service will be registered as outlet on the inlet."""
        self.log.debug('Setting Inlet to %s' % inlet)
        self.inlet = inlet
        if recursiveCall:
            self.inlet.addOutlet(self)

    def start(self):
        startDefer = Deferred()
        def _started(target):
            startDefer.callback(self)

        d = maybeDeferred(self._start)
        d.addCallback(_started)

        return startDefer


    def _start(self):
        """Override this and actually start the service"""
        raise(NotImplementedError)

    def _findObjectInInletChainOfClass(self,searchedClass):
        """
        tries to find an object in the chain of inlets which is a instance of searchedClass

        recurse through the inlet chain and find the first matching object that is an instance of
        the supplied class.

        Args:
            searchedClass: The class to look for

        Returns: 
            the first matching instance or None if None is found.
        """
        self.log.debug('Searching %s' % searchedClass)
        
        if(isinstance(self.inlet,searchedClass)):
            return self.inlet
        else:
            found = None
            try:
                found = self.inlet._findObjectInInletChainOfClass(searchedClass)
            except AttributeError:
                pass
            return found



class KNDistributor(KNOutlet):
    """Distribute Stream data from inlet to 1 or more outlets and handle
    errors in the chain of outlets.

    TODO:
    - What happens if no autostart desired
    - Which KNDistributor can start the chain of start/stop
    - Handling of crashes in chain
    - Stop behaviour: Let children finish writing stuff
    - Start behaviour: Start outlets first or inlets first

    """
    implements(IKNOutlet, IKNInlet)

    def __init__(self, name=None):
        super(KNDistributor, self).__init__(name=name)

        self.inlet = None
        self.outlets = []        


    # Dataflow .. Inlet and outlets
    def __setattr__(self,name,value):
        if name == 'inlet':
            if self.running:
                raise(Exception('Can only change inlet if not running.'))
            elif value is not None:
                self.__dict__[name] = IKNInlet(value)
                self.inlet.addOutlet(self)
            else:
                self.__dict__[name] = None
        else:
            self.__dict__[name] = value




    def setInlet(self,inlet,recursiveCall=True):
        """Set the inlet of this service. This can only be changed when the service is stopped. The inlet is the datasource or input.
        If not already done this service will be registered as outlet on the inlet."""
        self.log.debug('Setting Inlet to %s' % inlet)
        self.inlet = inlet
        if recursiveCall:
            self.inlet.addOutlet(self)


    def addOutlet(self,outlet):
        """Outlets receive data from the service when the service is running. Outlets need to be of type IKNOutlet.
        If not already done this service will be set as inlet on the specified outlet."""
        #
        self.log.debug('Adding outlet %s to %s' % (outlet,self))
        # print "Self.outlets:%s (%s)" % (self.outlets,id(self.outlets))
        # print "Outlet.outlets: %s (%s)" % (outlet.outlets,id(outlet.outlets))
        # return()
        if IKNOutlet.providedBy(outlet):
            if outlet.inlet != self:
                outlet.setInlet(self,recursiveCall=False)
            if outlet not in self.outlets:
                if outlet is not self:
                    self.outlets.append(outlet)
                    # print "Self.outlets:%s" % self.outlets
                    # print "Outlet.outlets: %s" % outlet.outlets
                else:
                    raise(Exception("Can't be an outlet of myself"))                    

        else:
            raise(Exception('%s does not implement %s' % (outlet,IKNOutlet)))

    def removeOutlet(self,outlet):
        """Remove the outlet from the list of outlets. The outlet will no longer receive any data."""
        if outlet in self.outlets:
            self.outlets.remove(outlet)
            outlet.inlet = None
            if outlet.running:
                raise(ServiceRunningWithouInlet)



    # Starting

    def start(self):
        """Start the module and all outlets. Notify the inlet when everything is running. Do not override this."""
        self.runningOutlets = 0

        defStarted = Deferred()
        if not self.inlet:
            raise(ServiceRunningWithouInlet)

        if not len(self.outlets):
            raise(ServiceRunningWithoutOutlets)

        if not self.running:

            self._willStart()

            # Start the outlets
            def _outletStarted(object):
                self.runningOutlets += 1
                if self.runningOutlets >= len(self.outlets):
                    #All outlets started
                    _allOutletsStarted()

            def _allOutletsStarted():
                self.running = True
                self._start()
                self.log.debug("Did start")
                self.log.debug("Will notify %s that I started" % self.inlet)
                self.inlet.start()
                defStarted.callback(self)
                self.log.debug("Started and notified %s" % self.inlet)
                self._didStartAndNotifiedInlet()

            for outlet in self.outlets:
                self.log.debug('Starting outlet %s' % outlet)
                d = maybeDeferred(outlet.start)
                d.addCallback(_outletStarted)
            if not len(self.outlets):
                _allOutletsStarted()
        else:
            self.log.warning("%s is already running. Can not start" % self)

        return defStarted

    def _willStart(self):
        """Stuff to be done before outlets gets the start command (implemented for IKNInlet)"""
        pass

    def _start(self):
        """Stuff to be done after all outlets have started but before the inlet is notified (IKNInlet)"""
        pass

    def _didStartAndNotifiedInlet(self):
        """Stuff to be done after all outlets have started and the inlet was notified (INKNInlet)"""
        pass

    def outletStarted(self,outlet):
        """called by our outlets after they started (IKNInlet)"""
        pass

    def _startFailed(self,outlet):
        pass

    def startRecording(self, autoStop=None):
        """Send 'startRecording' message to every outlet that conforms to IKNRecorder. IKNRecorder implementations make streams persistent.
        Keyword Arguments:
        autoStop: Automatically stop this recording in x seconds
        """
        self.log.info('Starting recording')
        for outlet in self.outlets:
            if IKNRecorder.implementedBy(outlet.__class__):
                if not outlet.recording:
                    outlet.startRecording()
                else:
                    outlet.log.warning('Already recording. Can not start again.')
            if autoStop:
                reactor.callLater(autoStop,outlet.stopRecording)

    def stopRecording():
        """Stop recording of the content. Also send 'stopRecording' to every outlet that conforms to IKNRecorder."""
        self.log.info('Stopping recording')
        for outlet in self.outlets:
            if IKNRecorder.implementedBy(outlet.__class__):
                if outlet.recording:
                    outlet.stopRecording()




    # Stopping

    def stop(self):
        """Stop the module and all outlets. Notify the inlet when everything has stopped. Do not override this."""
        self.log.debug("Will stop")
        self._willStop()

        self.log.debug("Did stop. Inlet %s not notified yet" % self.inlet)
        self._didStop()

        self.log.debug("Did stop. Will notify inlet %s" % self.inlet)
        self.inlet._outletStopped(self)

        self.log.debug("Did stop. Inlet %s notified" % self.inlet)
        self._didStopAndNotifiedInlet()

    def _willStop(self):
        """Stuff to be done before outlets get the stop command"""
        pass

    def _didStop(self):
        """Stuff to be done after outlets stopped but before the inlet is notified."""
        pass

    def _didStopAndNotifiedInlet(self):
        """Stuff to be done after outlets stopped and after the inlet was notified"""
        pass

    def _outletStopped(self,outlet):
        """The outlet notified us that it has stopped"""
        pass


    # IKNInlet - Produce data
    def sendDataToAllOutlets(self,data):
        """Send data to our outlets"""
        for outlet in self.outlets:
            outlet.dataReceived(data)

    # INKOutlet - Consume data

    def dataReceived(self,data):
        """The inlet Chain writes data to this method. Overwrite it and do something meaningfull with it"""
        self.sendDataToAllOutlets(data)


class KNProcessProtocol(protocol.ProcessProtocol):
    """Base class for all process Protocols"""
    def __init__(self, name='Unknown'):
        self.name = name
        self.factory = None
        self._lastLogLine = None
        self.log = logging.getLogger('[%s]' % (self.__class__.__name__))

    def errReceived(self,data):
        """This is STDERR of the process. Everything gets written to the log. If this is usefull information override this method"""
        lines = str(data).splitlines()
        #log.msg(data)
        for line in lines:
            self._lastLogLine = line
            self.log.warn("%s" % (line))

    def writeData(self,data):
        """Write data to STDIN"""
        self.transport.write(data)

    def processEnded(self, reason):
        if(reason.value.exitCode):
            self.log.error("crashed")
            self.log.error("Process was: %s" % (self.factory.cmdline))
            self.log.error("Last message: %s" % (self._lastLogLine))
            if "processCrashed" in dir(self.factory):
                self.factory.processCrashed()
        else:
            self.log.info("ended.")  
