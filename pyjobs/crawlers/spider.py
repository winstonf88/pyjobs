from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from tornado import gen
from tornado import httpclient
from tornado.queues import Queue

import logging

logger = logging.getLogger(__name__)


class BaseSpider(object):
    url_parser = None

    def __init__(self, engine, concurrent=3):
        self.engine = engine
        self.http = httpclient.AsyncHTTPClient()
        self.queue = Queue()
        self.concurrency = concurrent

    @property
    def hostname(self):
        return self.url_parser.hostname

    @property
    def url_root(self):
        return self.url_parser.url_root

    @property
    def base_url(self):
        return self.url_parser.base_url

    @gen.coroutine
    def __worker(self):
        """Consumes the queue."""
        while True:
            yield self.fetch_url()

    @gen.coroutine
    def crawl(self, description, location):
        """Starts crawling the specified URL."""
        url = self.url_parser(description, location)
        self.queue.put(url)
        self.engine.notify_started(self)
        for _ in range(self.concurrency):
            self.__worker()
        yield self.queue.join()
        self.engine.notify_finished(self)

    @gen.coroutine
    def fetch_url(self):
        """Retrieves a URL from the queue and returns the parsed data."""
        url = yield self.queue.get()
        logger.info('fetching %s' % url)
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
        except (httpclient.HTTPError, ValueError):
            message = 'HTTP Error: (%s)' % url
            self.engine.write_message(message, self.engine.STATUS_ERROR)
        else:
            self.engine.write_data(data)
        finally:
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
