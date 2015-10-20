import logging
from tornado import gen
from tornado import web
from tornado import websocket
from pyjobs.crawlers.consumer import crawl_jobs
from pyjobs.utils import json

logger = logging.getLogger(__name__)


class WebSocketHandler(websocket.WebSocketHandler):

    @gen.coroutine
    def open(self):
        logger.info('new connection')

    @gen.coroutine
    def on_message(self, message):
        cmd = json.loads(message)
        if cmd['cmd'] == 'search':
            logger.info('cmd: search')
            yield crawl_jobs(self)

    def on_close(self):
        logger.info('close connection')

    def write_message(self, message, binary=False):
        data = json.dumps(message)
        return super(WebSocketHandler, self).write_message(data, binary)

class HomeHandler(web.RequestHandler):

    @gen.coroutine
    def get(self):
        self.render('templates/home.html')
