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

        return "codene"

    def completeCall(self, response, request):
        # return a response

        request.write(response)
        request.finish()

    def render_POST(self, request):
        d = defer.maybeDeferred(
            # Call the API 
        )

        d.addCallback(self.completeCall, request)

        return server.NOT_DONE_YET
