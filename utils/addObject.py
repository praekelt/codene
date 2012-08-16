#!/usr/bin/python
import urllib, urllib2, mimetypes
import sys


fn = sys.argv[1]

content_type = mimetypes.guess_type(fn)[0]

request = urllib2.Request("http://localhost:8080/test/%s" % fn, data=open(fn).read())
request.add_header('Content-Type', content_type)
request.get_method = lambda: 'PUT'

res = urllib2.urlopen(request).read()
print res
