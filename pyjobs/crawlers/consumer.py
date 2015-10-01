import logging
from tornado import gen
from pyjobs.crawlers.pyorg import PyORGCrawlwer

logger = logging.getLogger(__name__)

CRAWLERS = [PyORGCrawlwer]


@gen.coroutine
def crawl_jobs(socket):
    logger.info('start crawling %s' % socket)
    yield [cls(socket).crawl() for cls in CRAWLERS]
    logger.info('end crawling')
