from tornado import gen

from pyjobs.crawlers.spider import BaseSpider
from pyjobs.utils import URLParser

import logging

logger = logging.getLogger(__name__)


class GithubCrawler(BaseSpider):
    url_parser = URLParser(url='https://jobs.github.com/positions')

    @gen.coroutine
    def fetch_links(self, response, soup):
        """Fetch next github page."""
        urls = []
        page = soup.find('a', {'class': 'js-paginate button'})
        if page:
            url = '%s%s' % (self.url_root, page.attrs['href'])
            urls.append(url)
        raise gen.Return(urls)

    @gen.coroutine
    def parse_response(self, response, soup):
        """Extract job info from response."""
        jobs = soup.find('table', {'class': 'positionlist'})
        data = []

        for job in jobs.findAll('tr'):
            if not job.find('td', {'class': 'title'}):
                continue

            date = job.find('span', {'class': 'when relatize'}).text
            date = date.split(' ')[0]
            title = job.find('a')

            data.append({
                'title': title.text.strip(),
                'company': job.find('a', {'class': 'company'}).text,
                'location': job.find('span', {'class': 'location'}).text,
                'tags': [],
                'category': '',
                'date': date,
                'origin': self.url_parser.hostname,
                'url': '%s%s' % (self.url_root, title.attrs['href']),
            })

        raise gen.Return(data)
