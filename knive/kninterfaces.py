import logging
from zope.interface import Interface, implements, Attribute

class IKNOutlet(Interface):
    """IKNOutlets receive data from IKNInlets and do something with it."""
    
    def dataReceived(data):
        """Handle the data received."""
        
    def setInlet(inlet):
        """Register a data sender (Inlet) with us. Inlet has to be of type IKNOutlet"""
        

class IKNInlet(Interface):
    """IKNInlets generate data in some way. They will send the data to registered IKNOutlets"""
    def addOutlet(outlet):
        """Register an outlet with us. The outlet has to be of type IKNOutlet"""
        
    def getStats():
        """Return a string with statistics about data flow (bits p second?)"""

    def outletStarted():
        """Our outlet is ready to receive data. Start the service. This effectivly is the start method of pure inlets."""
        


class IKNRecorder(IKNOutlet):
    """A special IKNOutlet that will make data persistent after startRecording is called. You need to supply an Episode object.
    Episodes store information such as 'starttime', 'endtime' and metadata for this recording."""
    def startRecording(episode,autoStop=None):
        """Start the recording of received data.
        Arguments:
        episode: The current episode that is to be recorded. Register this recording with the episode by calling episode.register(IKNRecording-instance)
        Keyword Arguments:
        autoStop: Automatically stop this recording in x seconds
        Returns:
        On success an IKNRecording object is returned.
        """

    def stopRecording():
        """Stop the recording process."""

class IKNRecording(Interface):
    """A recording stores information that is specific for a stream and single moment in time. An episode object is assigned to this recording."""
    episode = Attribute("""Episode object this recording belongs to""")



        