from twisted.internet import defer
from riakasaurus import riak

import hashlib
import hmac
import base64

from codene import util

class API(object):
    def __init__(self):
        self.client = riak.RiakClient()

    def getCanonicalPath(self, request):
        path = request.path.strip('/')

        host = request.getRequestHostname()

        #XXX make configurable
        myHost = 'cdn.r53.praekelt.com'

        # Add bucket name from host to path
        path = ''
        if host.strip(myHost):
            bucket = host.split('.')[0]
            path += '/'+bucket

        path += request.path
        return path

    def getSignRequest(self, verb, request, secret):
        # Creates an HMAC sig for a request

        contentType = util.getHeader(request, 'content-type')
        contentMD5 = util.getHeader(request, 'content-md5')

        date = util.getHeader(request, 'date')
        amzDate = util.getHeader(request, 'x-amz-date')

        if amzDate:
            date = 'x-amz-date:%s' % amzDate

        path = self.getCanonicalPath(request)

        signData = ['PUT', contentMD5, contentType, date, path]

        sig = hmac.new(
            key = secret,
            msg = '\n'.join(signData),
            digestmod = hashlib.sha1
        ).digest()

        return base64.b64encode(sig)

    def getSecret(self, key):
        fake = {
            'testac': 'secret'
        }
        return fake[key]

    @defer.inlineCallbacks
    def get(self, bucket, name):
        meta = self.client.bucket('%s_meta' % bucket)
        objects = self.client.bucket('%s_objects' % bucket)

        metadata = (yield meta.get(name)).get_data()

        metadata['object'] = (yield objects.get_binary(metadata['link'])).get_data()

        defer.returnValue(metadata)

    @defer.inlineCallbacks
    def put(self, bucket, name, cType, data):
        obref = uuid.uuid1().hex
        datahash = hashlib.md5(data).hexdigest()

        meta = self.client.bucket('%s_meta' % bucket)
        objects = self.client.bucket('%s_objects' % bucket)

        metadata = {
            'filename': name, 
            'checksum': datahash, 
            'content-length': len(data),
            'content-type': cType,
            'link': obref
        }

        objmeta = meta.new(name, metadata)

        obj = objects.new_binary(obref, data, content_type="text/binary")

        # Make sure the real object stores before we store the metadata
        yield obj.store()
        yield objmeta.store()

        print "Stored", name, datahash
        
        defer.returnValue('OK')
