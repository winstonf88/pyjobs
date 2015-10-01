import logging
from tornado import gen
from tornado import httpclient
from tornado.queues import Queue
from pyjobs.utils import json

logger = logging.getLogger(__name__)


class BaseSpider(object):
    URL = ''

    def __init__(self, socket, maxsize=3):
        if not self.URL:
            raise ValueError('No URL')

        self.socket = socket
        self.http = httpclient.AsyncHTTPClient()
        self.queue = Queue(maxsize=maxsize)

    @gen.coroutine
    def crawl(self):
        yield self.queue.put(self.URL)
        yield self.consume()
        yield self.queue.join()
        logger.info('Done')

    @gen.coroutine
    def fetch_url(self):
        url = yield self.queue.get()
        logger.info('fetching %s' % url)
        message = {'type': 'data', 'json': [], 'status': 'error'}
        try:
            response = yield self.http.fetch(url)
            logger.info('got response %s' % url)
            message['json'] = self.parse_response(response)
            message['status'] = 'success'
        except (httpclient.HTTPError, ValueError):
            message['message'] = 'http error'
        finally:
            self.socket.write_message(json.dumps(message))
            self.queue.task_done()

    @gen.coroutine
    def consume(self):
        while not self.queue.empty():
            yield self.fetch_url()

    def parse_response(self, response):
        raise NotImplementedError
