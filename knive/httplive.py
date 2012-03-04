import os
from foundation import KNDistributor


class HTTPLiveStream(KNDistributor):
    """A HTTPLiveStream accepts mpeg-ts streams (optionally) reencodes the data to (optionally) various qualities and cuts them in pieces.
    The resul are small .ts files of several seconds duration. The HTTPLiveStream creates a playlist over the created .ts files.
    The .ts segments and playlist are then typically stored on a webserver. Clients supporting HTTPLiveStream specification can then display
    the stream. See http://tools.ietf.org/html/draft-pantos-http-live-streaming for full specification."""
    
    
    def __init__(self,name='Unknown',destdir=None,channel=None,publishURL=None,lastIndex=1):
        """
        KWargs:
        name: Name of the stream. (Set by channel.name if not set and channel available)
        destdir: The location of resulting output files
        lastIndex is the index of the first index in a resulting new M3U8 file. It is where a
        previous segmenter for the same stream left the work. For Livestreams
        it's important to save it since the stream may be interrupted. Also, the same
        moment in time should result in the same index for every VariantStream to make
        adaptive Quality work. For the case that a VariantStream dies it shall restart with
        the biggest StartIndex at that given time (over all other variant streams). Therefore
        each variantStream updates this value.
        """
        self.name = name
        if channel and name != 'Unknown':
            self.name = channel.name
        super(HTTPLiveStream, self).__init__(name=self.name) # Call this after we have a name.

        self._destdir = None
        if not destdir:
            raise Exception('destdir can not be none.')
        self.setDestdir(destdir)

        self.publishURL = publishURL
        self._lastIndex = lastIndex
        
    def addQuality(self,name=None,config=None):
        """docstring for addQuality"""
        self.logger.info('\tQuality: %s' % name)
        #httpliveStream = HTTPLiveVariantStream('%s/%s' % (self.name,name))
        #httpliveStream.setInlet(self)
        #httpliveStream.setEncoder(None)
        # variantStream.setEncoder()
        
    
    def setLastIndex(self,lastIndex):
        """Update self.lastIndex if it's larger than the current value. This is called by variant streams everytime they write a segment."""
        if (lastIndex > self._lastIndex):
            self._lastIndex = lastIndex

    def setDestdir(self,destdir,createDir=False):
        """docstring for setDestdir"""
        self._destdir = os.path.abspath(destdir)
        if os.path.exists(destdir):
            self._destdir = destdir
            self.log.debug("Will create files in '%s'" % self._destdir)
        else:
            if(createDir):
                try:
                    os.mkdir(destdir)
                    self.setDestdir(destdir)
                except:
                    raise
            else:
                raise Exception("Directory does not exist %s" % destdir)