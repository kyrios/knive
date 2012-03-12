#
# kninterfaces.py
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

"""
INKOutlets are consumers of data.
IKNInlets are producers of data.
Most objects are both.

.. moduleauthor:: Thorsten Philipp <kyrios@kyri0s.de>

"""
from zope.interface import Interface, Attribute

class IKNStreamObject(Interface):
    """An object implementing :class:`IKNStreamObject` produces or consumes data.
    These objects can be started and stopped."""

    running = Attribute("""Indicating wheter the StreamObject is running or not""")

    def start():
        """Start the StreamObject. Consume/Produce data. Notify outlets if there are any."""

    def stop():
        """Stop the StreamObject. Stop consuming/producing data. Notify outlets if there are any. Notify our IKNInlet if we have one."""


class IKNOutlet(IKNStreamObject):
    """IKNOutlets receive data from IKNInlets and do something with it."""
    
    inlet = Attribute("""The IKNInlet object sending us data. This shall be set by :method:`setInlet`""")

    def dataReceived(data):
        """Handle the data received."""
        
    def setInlet(inlet):
        """Register a data sender (Inlet) with us. Inlet has to be of type IKNOutlet"""


        

class IKNInlet(IKNStreamObject):
    """IKNInlets generate data in some way. They will send the data to registered IKNOutlets dataReceived method."""

    outlets = Attribute("""List of registered outlets""")

    def addOutlet(outlet):
        """Register an outlet with us. The outlet has to be of type IKNOutlet"""

    def removeOutlet(outlet):
        """Remove an outlet from us."""
        
    def getStats():
        """Return a string with statistics about data flow (bits p second?)"""

    def outletStarted(outlet):
        """One of our outlets is ready to receive data."""




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



        