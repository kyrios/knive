from kninterfaces import *

class KNDistributor(object):
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

    def __init__(self, name=None, inlet=None, outlets=[]):
        super(KNDistributor, self).__init__()
        self.running = False
        self.name = name
        self.inlet = inlet
        self.outlets = outlets
        
        self.log = logging.getLogger('[%s] %s' % (self.__class__.__name__,self.name))

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.__instance__

    # Dataflow .. Inlet and outlets
    def __setattr__(self,name,value):
        if name == 'inlet':
            if self.running:
                raise(Exception('Can only change inlet if not running.'))
            elif value is not None:
                self.__dict__[name] = IKNInlet(value)
            else:
                self.__dict__[name] = None
        else:
            self.__dict__[name] = value

    def setInlet(self,inlet):
        """Set the inlet of this service. This can only be changed when the service is stopped. The inlet is the datasource or input.
        If not already done this service will be registered as outlet on the inlet."""
        self.inlet = inlet
        self.inlet.addOutlet(self)


    def addOutlet(self,outlet):
        """Outlets receive data from the service when the service is running. Outlets need to be of type IKNOutlet.
        If not already done this service will be set as inlet on the specified outlet."""
        if IKNOutlet.implementedBy(outlet.__class__):
            if outlet.inlet != self:
                outlet.inlet.setInlet(self)
            if outlet not in self.outlets:
                self.outlets.append(outlet)
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
        runningOutlets = 0

        defStarted = internet.defer()
        if not self.inlet:
            raise(ServiceRunningWithouInlet)

        if not self.running:
            self.log.debug("Will start")
            self.willStart()

            # Start the outlets
            def _outletStarted():
                runningOutlets += 1
                if runningOutlets >= len(self.outlets):
                    #All outlets started
                    _allOutletsStarted()

            def _allOutletsStarted():
                self.running = True
                self.log.debug("Did start")
                self.didStart()

                self.log.debug("Will notify %s that I started" % self.inlet)
                self.inlet.outletStarted(self)
                defStarted.callback()

                self.log.debug("Started and notified %s" % self.inlet)
                self.didStartAndNotifiedInlet()


            for outlet in self.outlets:
                d = outlet.start()
                d.addCallback(_outletStarted)
        else:
            self.log.warning("%s is already running. Can not start" % self)
            d.errback('%s is already running. Can not start' % self)

        return defStarted

    def willStart(self):
        """Stuff to be done before outlets gets the start command"""
        pass

    def didStart(self):
        """Stuff to be done after all outlets have started but before the inlet is notified"""
        pass

    def didStartAndNotifiedInlet(self):
        """Stuff to be done after all outlets have started and the inlet was notified"""
        pass

    def outletStarted(self,outlet):
        """called by our outlets after they started"""
        pass

    def startFailed(self,outlet):
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
        self.willStop()

        self.log.debug("Did stop. Inlet %s not notified yet" % self.inlet)
        self.didStop()

        self.log.debug("Did stop. Will notify inlet %s" % self.inlet)
        self.inlet.outletStopped(self)

        self.log.debug("Did stop. Inlet %s notified" % self.inlet)
        self.didStopAndNotifiedInlet()

    def willStop(self):
        """Stuff to be done before outlets get the stop command"""
        pass

    def didStop(self):
        """Stuff to be done after outlets stopped but before the inlet is notified."""
        pass

    def didStopAndNotifiedInlet(self):
        """Stuff to be done after outlets stopped and after the inlet was notified"""
        pass

    def outletStopped(self,outlet):
        """The outlet notified us that it has stopped"""
        pass


    # Data handling

    def dataReceived(self,data):
        """The inlet Chain writes data to this method. Overwrite it and do something meaningfull with it"""
        pass

