from twisted.internet import defer
from riakasaurus import riak
import simplejson, cgi, uuid, hashlib, time, math, os

class API(object):
    def __init__(self):
        self.client = riak.RiakClient()


    @defer.inlineCallbacks
    def put(self, bucket, name, data):
        obref = uuid.uuid1().hex
        datahash = haslib.md5(data)

        meta = self.client.bucket('%s_meta' % bucket)
        objects = self.client.bucket('%s_objects' % bucket)

        metadata = {
            'filename': name, 
            'bucket': bucket, 
            'checksum': datahash, 
            'link': obref
        }

        objmeta = meta.new(name, metadata)

        obj = objects.new(obref, data)
        
        # Make sure the real object stores before we store the metadata
        yield obj.store()
        yield objmeta.store()
        
