#
# channels.py
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

import root
from twisted.web import error



class Channels(root.KniveJsonApiResource):
    """All the channels"""

    channelsCache = {}
    backend = None

    def setup(self, backend):
    	self.backend = backend

    def getChild(self, channel, request):
        if path in self.channelsCache:
            return self.channelsCache[channel]
        elif path in self.backend.channels:
            self.channelsCache[channel] = self.backend.channels[channel]
            return self.channelsCache[channel]
        else:
            return error.NoResource()

    def _GET(self, request):
        for channel in self.backend.channels:
            yield {'name': channel.name, 'slug': channel.slug, 'episodes': channel.episodes, 'url': channel.url, 'recording': channel._recording}

