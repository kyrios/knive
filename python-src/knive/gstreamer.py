#
# gstreamer.py
# Copyright (c) 2012 Robert Weidlich <dev@robertweidlich.de>
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

from zope.interface                 import implements
from twisted.python                 import log
from twisted.internet.interfaces    import ILoggingContext
from twisted.internet.defer         import Deferred 

import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst

import hashlib
import random       

class GstInlet(KNInlet):
    """
       A gateway from gstreamer to knive

       with inspiration from
       http://gstreamer-devel.966125.n4.nabble.com/appsink-appsrc-pad-problems-oh-my-td972828.html

       Last element in the supplied pipeline has to be the "appsink" with the name "sink".
       
       TODO: 
       - set correct caps to ensure mpegts is the result
       - catch errors
       - clean stopping of streams
    """

    def __init__(self, name='unknown gst-source', pipeline="audiotestsrc ! audioconvert ! lame ! ffmux_mpegts ! appsink name=\"sink\""):
        super(GstInlet, self).__init__(name=name)
        self.pipeline = pipeline
        log.msg("initializing", system=self.name)

    def outletStarted(self,outlet):
        """Stuff to be done after all outlets have started but before the inlet is notified"""
        log.msg("Starting", system=self.name)

    def _start(self):
        self.player.set_state(gst.STATE_PLAYING)

    def _willStart(self):
        """Stuff to be done before outlets get the stop command"""
        log.msg("building gstreamer pipeline", system=self.name)
        self.player = gst.parse_launch(self.pipeline)
        sink = self.player.get_by_name("sink")
        #caps = gst.Caps("video/x-raw-gray,bpp=16,endianness=1234,width=320,height=240,framerate=(fraction)10/1")
        #sink.set_property('caps',caps)
        sink.set_property('blocksize', 64)
        sink.set_property('emit-signals', True)
        sink.connect("new-preroll", self.new_preroll)
        sink.connect("new-buffer", self.new_buffer)
        sink.connect("eos", self.eos)

    def new_preroll(self, appsink):
        log.msg("prerolling", system=self.name)
        buffer = appsink.emit('pull-preroll')
        #log.msg("BUFFER PREROLL LENGTH: %s" % len(buffer), system=self.name)
        self.streamheading(buffer)

    def new_buffer(self, appsink):
        #log.msg("new buffering", system=self.name)
        buffer = appsink.emit('pull-buffer')
        #log.msg("NEW BUFFER LENGTH: %s" % len(buffer), system=self.name)
        self.streamheading(buffer)

    def streamheading(self, buffer):
        #if not self.streamheader:
        #    # check caps for streamheader buffers
        #    caps = buffer.get_caps()
        #    print "CAPS: ", caps
        #    s = caps[0]
        #    if s.has_key("streamheader"):
        #        self.streamheader = s["streamheader"]
        #        self.debug("setting streamheader")
        #        for r in self.requests:
        #            self.debug("writing streamheader")
        #            for h in self.streamheader:
        #                r.write(h.data)
        #log.msg(str(type(buffer))+str(dir(buffer)), system=self.name)
        self.sendDataToAllOutlets(buffer.data)
    
    def eos(self, appsink):
        log.msg("eos", system=self.name)
