import logging
import os
import sys
from tornado import ioloop
from tornado import web

from pyjobs import handlers

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static/')

url_patterns = [
    web.url('/', handlers.HomeHandler, name='home'),
    web.url('/ws', handlers.WebSocketHandler),
    web.url('/static/(.*)', web.StaticFileHandler, {'path': STATIC_PATH}),
]

settings = {
    'compiled_template_cache': False,
}


def server():
    logger.info('Serving on port 8888')
    application = web.Application(url_patterns, **settings)
    application.listen(8888)
    ioloop.IOLoop.current().start()

if __name__ == '__main__':
    server()
