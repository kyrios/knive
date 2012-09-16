#
# apiV1.py
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


from twisted.web.resource import Resource
import json
import types


class KniveJsonApiResource(Resource):
    def __init__(self, *args, **kwargs):
        Resource.__init__(self)
        self.backend = args[0]
        try:
            self.setup(*args, **kwargs)
        except AttributeError:
            pass

    def render_GET(self, request):
        returnValue = self._GET(request)
        if (isinstance(returnValue, types.GeneratorType)):
            return self.jsonResponse(request, list(returnValue))
        else:
            return self.jsonResponse(request, returnValue)

    def render_PUT(self, request):
        data = json.loads(request.content.getvalue())
        returnValue = self._PUT(request, data)
        if (isinstance(returnValue, types.GeneratorType)):
            return self.jsonResponse(request, list(returnValue))
        else:
            return self.jsonResponse(request, returnValue)

    def jsonResponse(self, request, data, success=True, statusMessage=None):
        jsondata = data
        request.setHeader('Content-Type', 'application/json')
        return json.dumps(jsondata)

import config
import channels


class Root(KniveJsonApiResource):
    """The root element of the WebAPI V1."""

    def render_GET(self, request):
        return 'APIV1'

    # def getChild(self, name, request):
    #     try:
    #         print 'Looking for %s in cache' % name
    #         return(self.channels[name])
    #     except KeyError:
    #         print 'Searching %s in channel objects' % name
    #         for channel in self.backend.channels:
    #             if channel.slug == name:
    #                 webChannel = WebChannel(channel)
    #                 self.channels[channel.slug] = webChannel
    #                 return webChannel
    #         print '%s not found' % name
    #     print request.postpath
    #     print request.prepath
    #     apiVersion = request.prepath[0]
    #     channel = request.prepath[1]
    #     print 'Requesting Channel %s' % channel
    #     return self.backend.channels

    def setup(self, *args, **kwargs):
        self.putChild('config', config.Config(self.backend))
        self.putChild('channel', channels.Channels(self.backend))
        # self.putChild('root', WebRootTree(self.backend))
