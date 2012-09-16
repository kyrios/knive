#
# web.py
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

from twisted.application    import service, internet
from twisted.python         import log
from twisted.web            import static, server
from twisted.web.server     import Site
from twisted.web.resource   import Resource
from twisted.internet       import reactor


from zope.interface                 import implements
from twisted.internet.interfaces    import ILoggingContext

import apiV1.root

# import broadcast
import logging
import os
import json


class WebKnive(service.Service):
    """Web(server) backend for Knive"""

    def __init__(self, hostname="localhost", port=8002, resourcepath=None, backend=None):
        self.hostname = hostname
        self.port = port
        self.backend = backend
        self.logger = logging.getLogger('Knive WebSite')
        if resourcepath:
            self.resourcepath = os.path.abspath(resourcepath)
        else:
            self.resourcepath = os.path.abspath("resources")

        self.root = static.File(self.resourcepath)
        self.root.putChild('apiV1', apiV1.root.Root(self.backend))
        self.root.putChild('graph', GraphNode(self.backend))

        #self.wsFact = broadcast.BroadcastServerFactory("ws://localhost:9002")
        # root.putChild("doc", static.File("/usr/share/doc"))
        # self.cometApi = Root('http://%s:%s/' % (self.hostname,self.port))

        self.site = internet.TCPServer(
                                            self.port, 
                                            server.Site(self.root)
                                        )
        # self.ws = internet.TCPServer(
        #                                     self.port+1,
        #                                     self.wsFact
        #                                     )
        # self.site.setServiceParent(self)
        # self.ws.setServiceParent(self)                                        
                                        
    def startService(self):
        """docstring for startService"""
        self.logger.info("Starting (Port: %s Shared Folder: %s)" % (self.port,self.resourcepath))
        self.site.startService()
        self.logger.info("Websocket Service (Port: %s" % (self.port+1))
        # self.ws.startService()
        self.running = 1
        
        
    def write(self,message):
        """docstring for write"""
        self.wsFact.logMessage(message)


def jsonResponse(data,success=True,statusMessage=None):
    jsondata = {}
    jsondata['payload'] = data
    jsondata['success'] = success
    jsondata['statusMessage'] = statusMessage
    return json.dumps(jsondata)


class KniveResource(Resource):
    """docstring for KniveResource"""
    def __init__(self, backend):
        Resource.__init__(self)
        self.backend = backend
        try:
            self.setup()
        except AttributeError:
            pass
            
class GraphNode(KniveResource):

    def render_stream(self, s):
        return "%s\\n%s" % (s.__class__.__name__, s.name)

    def render_outlets(self, stream, graph):
        s = ""
        if hasattr(stream, 'outlets'):
            for o in stream.outlets:
                s += "%s.addEdge(\"%s\", \"%s\", { directed: true });\n" % (graph, self.render_stream(stream), self.render_stream(o))
                s += self.render_outlets(o, graph)
        return s

    def render_inlet(self, stream, graph):
        s = ""
        if hasattr(stream, 'inlet'):
            s += "%s.addEdge(\"%s\", \"%s\", { directed: true });" % (graph, self.render_stream(stream.inlet), self.render_stream(stream))
            s += self.render_inlet(stream.inlet, graph)
        return s

    def render_GET(self, request):
        self.i = 0
        s = "<html><head>"
        s += "<script type=\"text/javascript\" src=\"%s\"></script>" % "http://dracula.ameisenbar.de/js/raphael-min.js"
        s += "<script type=\"text/javascript\" src=\"%s\"></script>" % "http://dracula.ameisenbar.de/js/graffle.js"
        s += "<script type=\"text/javascript\" src=\"%s\"></script>" % "http://dracula.ameisenbar.de/js/graph.js"
        s += "</head><body><h1>Knive</h1><h2>Channel</h2>"
        s += "<ul>"
        for c in self.backend.channels:
            s += "<li>%s" % str(c)
            s += "<div id=\"canvas_%s\"></div></li>" % c.slug
        s += "</ul>"
        s += "<script type=\"text/javascript\">\nvar width = 800; var height = 600;\nwindow.onload = function() {\n"
        for c in self.backend.channels:
            s += "var g_%s = new Graph();\n" % c.slug
            s += self.render_inlet(c, "g_%s" % c.slug)
            s += self.render_outlets(c, "g_%s" % c.slug)
            s += "var layouter_%s = new Graph.Layout.Spring(g_%s);\n" % (c.slug, c.slug)
            s += "layouter_%s.layout();\n" % c.slug
            s += "var renderer_%s = new Graph.Renderer.Raphael('canvas_%s', g_%s, width, height);\n" % (c.slug, c.slug, c.slug)
            s += "renderer_%s.draw();\n" % c.slug
        s += "};</script>"
        s += "</body></html>"
        return s
                

class WebRootTree(KniveResource):
    """docstring for WebRootTree"""

    def render_GET(self,request):
        """docstring for render_GET"""
        returnSon = {}
        returnSon['success'] = True
        returnSon['root'] = {}
        returnSon['root']['expanded'] = True
        returnSon['root']['childen'] = []
        for stream in self.backend.streams:
            child = {}
            child['text'] = stream.name
            child['leaf'] = True
            returnSon['root']['childen'].append(child)
            
        return json.dumps(returnSon)


                    
        
    
if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG)
    loggingObserver = log.PythonLoggingObserver()
    loggingObserver.start()
    
    

    webservice = WebKnive(port=9001,backend=backend,resourcepath='/Users/thorstenphilipp/Dropbox/projects/HTTP-Live-Streaming/knive/resources')
    webservice.setServiceParent(knive)


    knive.startService()


    reactor.run()
