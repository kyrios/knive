import os
from foundation import KNDistributor
from ffmpeg     import FFMpeg


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
        if channel.name and name == 'Unknown':
            self.name = channel.name
        super(HTTPLiveStream, self).__init__(name=self.name) # Call this after we have a name.

        self._destdir = None
        if not destdir:
            raise Exception('destdir can not be none.')
        self.setDestdir(destdir)

        self.publishURL = publishURL
        self._lastIndex = lastIndex
        self.qualities = []

    def createQuality(self,name,config,ffmpegbin=None):
        """Create a new HTTPLiveVariantStream object and add it to self.qualities.
        Args:
        name: Give this Quality a name. This will be used in paths. So beware.
        config: A valid configobject for setup of this quality.

        Return:
        The created HTTPLiveVariantStream"""
        self.log.info('Creating new HTTPLiveVariantStream: %s' % name)
        httpliveStreamvariant = HTTPLiveVariantStream('%s/%s' % (self.name,name),config,ffmpegbin=ffmpegbin)
        self.addQuality(httpliveStreamvariant)
        return httpliveStreamvariant

        
    def addQuality(self,quality):
        """Add the HTTPLiveVariantStream object 'quality' to self.qualities"""
        # TODO: Fix/Check behaviour when already running. What happens?
        if quality not in self.qualities:
            self.qualities.append(quality)

    def removeQuality(self,quality):
        """Remove a quality from the stream. This is tricky (?) when the stream is running"""
        raise(NotImplemented)
        
   
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

class HTTPLiveVariantStream(KNDistributor):
    """Encode an input mpegts stream to the desired quality and segment the stream to chunks"""
    
    def __init__(self,name,encoderArguments,destdir=None,ffmpegbin=None):
        """Set up a new HTTP Live Stream Variant
        Args:
        name: Name of this quality (Used in path names)
        encoderArguments: ConfigObject for FFMpeg options.
        destdir: The location where files are saved. If None it's derived from the paret HTTPLiveStream and 'name' of the variant (recommended)"""
        super(HTTPLiveVariantStream,self).__init__(name=name)
        self.name = name
        self._encoder = None
        self._segmenter = None
        # Set up the encoder
        if ffmpegbin:
            self._encoder = FFMpeg(ffmpegbin=ffmpegbin,encoderArguments=encoderArguments)
        else:
            self._encoder = FFMpeg(encoderArguments=encoderArguments)



        # self._segmenter = HTTPLiveSegmenter()
        # Hook everything up
        self.addOutlet(self._encoder)
        # self._encoder.addOutlet(self._segmenter)

        
    def setDestdir(self,destdir,createDir=False):
        """docstring for setDestdir"""
        if destdir is None:
            return #TODO: Bug somewhere here... X_X
        destdir = os.path.abspath(destdir)
        if os.path.exists(destdir):
            super(HTTPLiveVariantStream,self).__setattr__('destinationDirectory',destdir)
            self.logger.debug("Will create files in '%s'" % self.destinationDirectory)
        else:
            if(createDir):
                try:
                    os.mkdir(destdir)
                    self.setDestdir(destdir)
                except:
                    raise
            else:
                raise Exception("Directory does not exist %s" % destdir)


# class HTTPLiveSegmenter(KNProcess):
#     """Cuts mpeg-ts streams in chunks and creates index files."""
#     def __init__(self,inlet,tempdir=None):
#         super(HTTPLiveSegmenter, self).__init__()
#         self.protocol = SegmenterProtocol()
#         inlet.addOutlet(inlet)
#         self.destdir = inlet
#         self.tempdir = tempdir
#         if self.tempdir is None:
#             self.tempdir = tempfile.gettempdir()
#         self.m3u8 = None 
#         self.httpStream = None
            
    
#     def startProcess(self):
#         """Starting the segmenter"""
#         self.httpStream = self.findParentOfType(HTTPLiveStream)
#         self.protocol.setName("segmenterProtocol")
#         self.protocol.setParent(self)
#         self.m3u8 = HTTPLiveStreamM3U8(self.destdir)
#         self.m3u8.setName("M3U8")
#         self.m3u8.setParent(self)
        
#         args = ["live_segmenter","10",self.tempdir,self.parent.parent.name,self.parent.parent.name]
#         self.logger.info("Spawning Process: %s" % " ".join(args))
#         reactor.spawnProcess(self.protocol,self.parent.parent.config.get('Paths','segmenter'),args)
    
#     def segmentReady(self,startindex,lastindex,end,encodingprofile,duration):
#         """A segment is ready for transfer"""
#         #umts-00000001.ts
#         duration = float(duration)
        
#         self.httpStream.setLastIndex(int(lastindex))
#         filename = "%s-%08d.ts" % (encodingprofile,int(lastindex))
#         sourcefile = "%s%s%s" % (self.tempdir,os.path.sep,filename)
#         destfile = "%s%s%s" % (self.destdir,os.path.sep,self.m3u8.addSegment(duration))
#         self.logger.debug("Copying file %s to %s" % (filename,destfile))
        
#         #FIXME: This is propably a blocking call!
#         shutil.move(sourcefile,destfile)
#         self.m3u8.writeIndexFile()
