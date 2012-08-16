#!/usr/bin/env/python
#
# channel.py
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

"""Channels are a collection of stream settings. Inputs, Outputs, Archiving

.. moduleauthor:: Thorsten Philipp <kyrios@kyri0s.de>

"""

from foundation import KNDistributor
from exceptions import AlreadyRecording, NoRecording
from episode    import Episode
from  kninterfaces import IKNRecorder

import sys, os
import time

class Channel(KNDistributor):
    """A channel (also called Stream or Show) is the central element. For example a podcast project or a room at a conference is a channel.
    Think in broadcast channels. One channel can only stream one thing at a time."""

    def __init__(self,name,configObj,slug,url=None):
        """
        Args:
            name: The name of this channel. Example: "Bits und so"
        
        Kwargs:
            slug: A short name for this channel. AlphaNumeric. The slug is used for stuff like filenames and in. Example: "bus"
            url: The website where more information about this channel can be found
        """

        super(Channel, self).__init__(name=name)
        self.config = configObj
        self.episodes = {}
        """Dictionary of episodes/recordings."""
        self.slug = slug
        self.url = url
        self.currentEpisode = None
        self._recording = False
        self._lastRecording = None
        self.destinationDirectory = self.config['paths']['knivedata'] + os.path.sep + self.slug
        if os.path.exists(self.destinationDirectory):
            self.log.debug("Will create files in '%s'" % self.destinationDirectory)
        else:
            try:
                os.mkdir(self.destinationDirectory)
            except:
                raise


    def __str__(self):
        return "%s/%s (%s) %s episodes" % (self.slug,self.name,self.url,len(self.episodes))


    def startEpisode(self,record=True):
        """Everything is an episode in knive. Want to start broadcasting? Start Episode!
        Kwargs:
        record: BOOL. Make the episode persistant. (e.g. HTTP Live Streams will provide a ReLive)
        """
        if not self._recording:
            self._recording = True
            episodeId = self._getNewEpisodeId()
            self.currentEpisode = Episode(self,episodeId)
            self.episodes[episodeId] = self.currentEpisode
            self.currentEpisode.start()
            if record:
                for outlet in self.outlets:
                    if IKNRecorder.providedBy(outlet):
                        print outlet
                        outlet.startRecording(self.currentEpisode)
            # else:
            #     for outlet in self.outlets:
            #         outlet.start
            linkTarget = self.currentEpisode.destinationDirectory
            linkName = self.destinationDirectory + os.path.sep + 'latest'

            if(os.path.exists(linkName)):
                os.unlink(linkName)
            os.symlink(linkTarget, linkName)

            return self.currentEpisode
        else:
            raise AlreadyRecording


    def stopEpisode(self,episode=None):
        """Stops a running recording."""
        if episode is None:
            episode = self.currentEpisode
        if self._recording:
            self._recording = False
            for outlet in self.outlets:
                if IKNRecorder.providedBy(outlet):
                    outlet.stopRecording()
            episode.stop()
        else:
            raise NoRecording


    def getMetadataAsJson(self):
        pass



    def _getNewEpisodeId(self):
        """Return a new unique episode Id"""
        return time.strftime('%Y-%m-%d_%H-%M-%S')
