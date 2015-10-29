from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from tornado import gen
from tornado import httpclient
from tornado.queues import Queue

from pyjobs.utils import json

import logging

logger = logging.getLogger(__name__)


class BaseSpider(object):
    URL = ''

    def __init__(self, socket, concurrent=3):
        if not self.URL:
            raise ValueError('No URL')
        url_parts = urlsplit(self.URL)
        self.domain = '%s://%s' % (url_parts.scheme, url_parts.hostname)
        self.socket = socket
        self.http = httpclient.AsyncHTTPClient()
        self.queue = Queue()
        self.concurrency = concurrent

    @gen.coroutine
    def __worker(self):
        """Consumes the queue."""
        while True:
            yield self.fetch_url()

    @gen.coroutine
    def crawl(self):
        """Starts crawling the specified URL."""
        self.queue.put(self.URL)
        for _ in range(self.concurrency):
            self.__worker()
        yield self.queue.join()

    @gen.coroutine
    def fetch_url(self):
        """Retrieves a URL from the queue and returns the parsed data."""
        url = yield self.queue.get()
        logger.info('fetching %s' % url)
        message = {'type': 'data', 'data': [], 'status': 'error'}
        try:
            response = yield self.http.fetch(url)
            soup = BeautifulSoup(response.body)
            logger.info('got response %s' % url)

            urls = yield self.fetch_links(response, soup)
            for new_url in urls:
                logger.debug('Added %s to queue' % new_url)
                yield self.queue.put(new_url)

            data = yield self.parse_response(response, soup)
            logger.info('Parsed response for %s' % url)
            message['data'] = data

            message['status'] = 'success'
        except (httpclient.HTTPError, ValueError):
            message['message'] = 'http error'
        finally:
            self.socket.write_message(message)
            self.queue.task_done()

    @gen.coroutine
    def fetch_links(self, response, soup):
        """Fetch URLs to be added to the queue."""
        raise gen.Return([])

    def parse_response(self, response, soup):
        """Extract information from the response, return should be a 
        list of dict's.
        
        Sample dict:
        {
            'title': 'Job Title',
            'company': 'Company Name',
            'location': 'City/State/Country',
            'tags': ['tag1', 'tag2', 'tag3'],
            'category': 'Software Developer',
            'origin': 'Name of the origin website',
            'url': 'Link to the complete job description',
        }
        """
        raise NotImplementedError
