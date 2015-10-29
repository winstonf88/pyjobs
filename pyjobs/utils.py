from urllib.parse import urlencode, urlsplit

try:
    import simplejson as json
except ImportError:
    import json


class URLParser(object):
    def __init__(self, url, description='description', location='location'):
        self.base_url = url
        self.desc = description
        self.location = location

        url_parts = urlsplit(url)
        self.hostname = url_parts.hostname
        self.url_root = '%s://%s' % (url_parts.scheme, url_parts.hostname)

    def __call__(self, description=None, location=None):
        params = {}
        query = ''

        if self.desc:
            desc = 'python %s' % description if description else 'python'
            params[self.desc] = desc
        if self.location and location:
            params[self.location] = location

        if params:
            query = urlencode(params)
        return '%s?%s' % (self.base_url, query)
