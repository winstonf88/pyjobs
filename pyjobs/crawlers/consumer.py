import logging
from tornado import gen

from pyjobs.crawlers.github import GithubCrawler
from pyjobs.crawlers.pyorg import PyORGCrawler
from pyjobs.crawlers.stackoverflow import StackOverflowCrawler

logger = logging.getLogger(__name__)

CRAWLERS = [GithubCrawler, PyORGCrawler, StackOverflowCrawler]


@gen.coroutine
def crawl_jobs(socket):
    """Start all spiders."""
    logger.info('start crawling %s' % socket)
    yield [cls(socket).crawl() for cls in CRAWLERS]
    logger.info('end crawling')
    socket.close()
