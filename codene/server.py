from twisted.application import internet, service
from twisted.web import static, server, resource, client
from twisted.internet import defer, reactor, threads, utils

from codene import api, util

class CodeneMixin(object):

    def render_PUT(self, request):
        # Put an object
        auth = util.getHeader(request, 'authorization')

        if not auth:
            return ''

        # Split the auth header 'blah key:sig' 
        key, sig = auth.split()[-1].split(':', 1)

        secret = self.api.getSecret(key)

        # Get the HMAC sig we have 
        sr = self.api.getSignRequest('PUT', request, secret)

        if sr != sig:
            return ''

        content = request.content

        contentType = util.getHeader(request, 'content-type', 'application/binary')

        path = self.api.getCanonicalPath(request).strip('/')

        # Figure out from here if it's an object put or bucket creation
        # Amazon's API is so "awesome" that there isn't much discernible difference

        if '/' in path:
            bucket, name = path.split('/',1)
        else:
            return "No bucket specified"

        # XXX This should stream the put into Riak somehow
        d = self.api.put(bucket, name, contentType, content.read()).addCallback(
            self.completeRequest, request
        ).addErrback(
            self.logError, request
        )

        return server.NOT_DONE_YET

class Server(resource.Resource, CodeneMixin):
    isLeaf = True
    addSlash = True

    def __init__(self):
        self.api = api.API()

    def render_GET(self, request):
        # For retrieving objects
        path = request.path.strip('/')

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
        request.setHeader('content-length', str(response['content-length']))
        
        request.write(response['object'])
        request.finish()

    def logError(self, error, request):
        error.printTraceback()

        request.write("ERROR")
        request.finish()

    def completeRequest(self, response, request):
        # Complete deferred request
        request.write(response)
        request.finish()

    def render_POST(self, request):
        # Would we do anything with post?
        return "Not implemented"
