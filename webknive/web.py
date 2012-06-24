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
        self.root.putChild('apiV1',WebAPIV1(self.backend))
       
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
    data['success'] = success
    data['statusMessage'] = statusMessage
    return json.dumps(data)


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

class WebAPIV1(KniveResource):
    """docstring for WebData"""

    def setup(self):
        self.channels = {}

    def getChild(self,name, request):
        try:
            print 'Looking for %s in cache' % name
            return(self.channels[name])
        except KeyError:
            print 'Searching %s in channel objects' % name
            for channel in self.backend.channels:
                if channel.slug == name:
                    webChannel = WebChannel(channel)
                    self.channels[channel.slug] = webChannel
                    return webChannel
        # print request.postpath
        # print request.prepath
        # apiVersion = request.prepath[0]
        # channel = request.prepath[1]
        # print 'Requesting Channel %s' % channel
        # print self.backend.channels
    # def setup(self):
    #     print 'Channel List'
    #     print self.backend.channels
    #     for channel in self.backend.channels:
    #         print '.....................%s' % channel
    #     sys.exit(1)
    #     self.putChild('channel',WebChannels(self.backend))
    #     self.putChild('root',WebRootTree(self.backend))



class WebChannel(Resource):
    """A API representation of a Knive.Channel object"""
    def __init__(self, channel):
        Resource.__init__(self)
        self.channel = channel

    def render_GET(self,request):
        print self.channel.config['channels']
        for outlet in self.channel.config['channels'][self.channel.name]['outlets']:
            print outlet
        return jsonResponse({'episodes':self.channel.episodes, 'qualities': None})

    def render_POST(self,request):
        # self.channel.
        return jsonResponse({'id':1})

                       
        
        
class WebChannels(KniveResource):
    """docstring for WebChannels"""
    
    def setup(self):
        """docstring for setup"""
        self.isLeaf = False
        
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