from foundation import KNDistributor

class Channel(KNDistributor):
    """A channel (also called Stream or Show) is the central element. For example a podcast project or a room at a conference is a channel.
    Think in broadcast channels. One channel can only stream one thing at a time."""

    def __init__(self,name,slug=None,url=None):
        """Args:
        Name: The name of this channel. Example: "Bits und so"
        Kwargs:
        slug: A short name for this channel. AlphaNumeric. The slug is used for stuff like filenames. Example: "bus"
        url: The website where more information about this channel can be found"""
        super(Channel, self).__init__(name=name)
        self.episodes = []
        """List of episodes/recordings"""
        self.slug = slug
        self.url = url

        self._recording = False
        self._lastRecording = None

    def __str__(self):
        return "%s/%s (%s) %s episodes" % (self.slug,self.name,self.url,len(self.episodes))


    def startRecording():
        """Starts a recording of the stream. Return an episode object if recording started."""
        if not self._recording:
            self._recording = True
            episode = Episode()
            self.episodes.append(episode)
            episode.start()
            for outlet in self.outlets:
                if IKNRecorder.providedBy(outlet):
                    outlet.startRecording()
            return episode

    def stopRecording():
        """Stops a running recording."""
        if self._recording:
            self._recording = False
            for outlet in self.outlets:
                if IKNRecorder.providedBy(outlet):
                    outlet.stopRecording()
            self.episodes[-1].stop()
