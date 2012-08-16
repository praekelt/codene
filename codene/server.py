from twisted.application import internet, service
from twisted.web import static, server, resource, client
from twisted.internet import defer, reactor, threads, utils

import simplejson, os, cgi

from codene import api

class Server(resource.Resource):
    isLeaf = True
    addSlash = True

    def __init__(self):
        self.api = api.API()

    def render_GET(self, request):
        # For retrieving objects
        path = request.path.strip('/')

        print "Request", path 

        if '/' in path:
            bucket, name = path.split('/',1)
        else:
            # Should be a 404 actually... 
            return "Invalid bucket" 

        d = self.api.get(bucket, name).addCallback(
            self.completeGet, request
        )

        return server.NOT_DONE_YET

    def completeGet(self, response, request):
        # Complete deferred request
        request.setHeader('content-type', str(response['content-type']))
        request.write(response['object'])
        request.finish()

    def render_PUT(self, request):
        # Put an object
        contentType = request.requestHeaders.getRawHeaders('content-type')[0]
        content = request.content

        path = request.path.strip('/')
        if '/' in path:
            bucket, name = path.split('/',1)
        else:
            return "No bucket specified"

        # XXX This should stream the put into Riak somehow
        d = self.api.put(bucket, name, contentType, content.read()).addCallback(
            self.completePut, request
        )

        return server.NOT_DONE_YET

    def completePut(self, response, request):
        # Complete deferred request
        request.write(response)
        request.finish()

    def render_POST(self, request):
        # Would we do anything with post?
        return "Not implemented"
