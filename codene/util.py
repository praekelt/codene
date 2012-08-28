
def getHeader(request, header, default=''):
    head = request.requestHeaders.getRawHeaders(header)
    if head:
        return head[0]
    else:
        return default
