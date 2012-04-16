from twisted.application    import service, internet
from twisted.python         import log
from twisted.web            import static, server
from twisted.web.server     import Site
from twisted.web.resource   import Resource
from twisted.internet       import reactor


from zope.interface                 import implements
from twisted.internet.interfaces    import ILoggingContext

import broadcast
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
        self.root.putChild('data',WebData(self.backend))
       
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


class KniveResource(Resource):
    """docstring for KniveResource"""
    def __init__(self, backend):
        Resource.__init__(self)
        self.backend = backend
        try:
            self.setup()
        except AttributeError:
            pass
            
    
                

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

class WebData(KniveResource):
    """docstring for WebData"""
    def setup(self):
        self.putChild('channel',WebChannels(self.backend))
        self.putChild('root',WebRootTree(self.backend))
        
        
        
class WebChannels(KniveResource):
    """docstring for WebChannels"""
    
    def setup(self):
        """docstring for setup"""
        self.isLeaf = True
        
    def render_GET(self,request):
        """docstring for render_GET"""
        returnSon = {}
        returnSon['success'] = True
        returnSon['channels'] = []
        for stream in self.backend.channels:
                stre = {}
                stre['id'] = 1
                stre['name'] = stream.name
                stre['slug'] = stream.slug
                stre['url'] = stream.url
                stre['episodes'] = []
                for episode in stream.episodes:
                    episo = {}
                    episo['index'] = episode.index
                    episo['title'] = episode.title
                    episo['startdate'] = episode.startdate
                    episo['enddate'] = episode.enddate
                    stre['episodes'].append(episo)
                    
                returnSon['channels'].append(stre)
        stre0 = {}
        stre0['id'] = 2
        stre0['name'] = 'Test0'
        stre0['slug'] = 'tes0'
        returnSon['channels'].append(stre0)
        return json.dumps(returnSon,indent=4)
                    
        
    
if __name__ == '__main__':
    
    logging.basicConfig(level=logging.DEBUG)
    loggingObserver = log.PythonLoggingObserver()
    loggingObserver.start()
    
    

    webservice = WebKnive(port=9001,backend=backend,resourcepath='/Users/thorstenphilipp/Dropbox/projects/HTTP-Live-Streaming/knive/resources')
    webservice.setServiceParent(knive)


    knive.startService()


    reactor.run()