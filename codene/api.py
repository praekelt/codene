from twisted.internet import defer
from riakasaurus import riak
import simplejson, cgi, uuid, hashlib, time, math, os

class API(object):
    def __init__(self):
        self.client = riak.RiakClient()

    @defer.inlineCallbacks
    def get(self, bucket, name):
        meta = self.client.bucket('%s_meta' % bucket)
        objects = self.client.bucket('%s_objects' % bucket)

        metadata = (yield meta.get(name)).get_data()

        metadata['object'] = (yield objects.get(metadata['link'])).get_data()

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
            'content-type': cType,
            'link': obref
        }

        objmeta = meta.new(name, metadata)

        obj = objects.new(obref, data)

        # Make sure the real object stores before we store the metadata
        yield obj.store()
        yield objmeta.store()

        print "Stored", name, datahash
        
        defer.returnValue('OK')
