# episode.py
#
#
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


import logging
import os
import os.path
import time


class Episode(object):
    """docstring for Episode"""

    def __init__(self, channel, name):
        super(Episode, self).__init__()
        self.channel = channel
        self.name = name
        self.log = logging.getLogger('[%s] %s' % (self.__class__.__name__, self.name))
        self.destinationDirectory = "%s%s%s" % (self.channel.destinationDirectory, os.path.sep, self.name)
        self.starttime = None
        self.endtime = None

    def start(self):
        self.starttime = time.time()
        self._initPath()

    def stop(self):
        self.endtime = time.time()

    def _initPath(self):
        destdir = os.path.abspath(self.destinationDirectory)
        if os.path.exists(destdir):
            self.log.debug("Will create files in '%s'" % destdir)
        else:
            try:
                os.mkdir(destdir)
                index = open(destdir + os.path.sep + 'index.html', 'w')
                index.write("""
                    <video width="320" height="240" controls="controls" autoplay="autoplay">
  <source src="httplive/wifi/stream.m3u8" type="video/mp4" />
  Your browser does not support the video tag.
</video>
                    """)
            except:
                raise

