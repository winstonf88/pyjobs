import logging
from tornado import gen

from pyjobs.crawlers.github import GithubCrawler
from pyjobs.crawlers.pyorg import PyORGCrawler
from pyjobs.crawlers.stackoverflow import StackOverflowCrawler

logger = logging.getLogger(__name__)

CRAWLERS = [GithubCrawler, PyORGCrawler, StackOverflowCrawler]


class SearchEngine(object):
    STATUS_SUCCESS = 'success'
    STATUS_ERROR = 'error'

    TYPE_DATA = 'data'
    TYPE_MESSAGE = 'message'
    TYPE_STATUS = 'status'

    def __init__(self, socket):
        self.socket = socket

    @gen.coroutine
    def search(self, description, location):
        """Start all spiders."""
        self.write_status('searching')
        yield [cls(self).crawl(description, location) for cls in CRAWLERS]
        self.write_status('done')

    def write(self, message, msg_type, status=None):
        status = status or self.STATUS_SUCCESS
        data = {'data': message, 'type': msg_type, 'status': status}
        self.socket.write_message(data)

    def write_data(self, data, status=None):
        self.write(data, self.TYPE_DATA, status)

    def write_message(self, message, status=None):
        self.write(message, self.TYPE_MESSAGE, status)

    def write_status(self, status):
        self.write(status, self.TYPE_STATUS, self.STATUS_SUCCESS)

    def notify_started(self, crawler):
        self.write_message('Searching %s' % crawler.url_parser.hostname)

    def notify_finished(self, crawler):
        self.write_message('Finished %s search' % crawler.hostname)

@gen.coroutine
def search(socket, params):
    """Start all spiders."""
    engine = SearchEngine(socket)
    description = params.get('description')
    location = params.get('location')
    yield engine.search(description, location)
