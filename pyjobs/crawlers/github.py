from tornado import gen
from pyjobs.crawlers.spider import BaseSpider

import logging

logger = logging.getLogger(__name__)


class GithubCrawlwer(BaseSpider):
    URL = 'https://jobs.github.com/positions?description=python'

    @gen.coroutine
    def fetch_links(self, response, soup):
        urls = []
        page = soup.find('a', {'class': 'js-paginate button'})
        if page:
            url = '%s%s' % (self.domain, page.attrs['href'])
            urls.append(url)
        raise gen.Return(urls)

    @gen.coroutine
    def parse_response(self, response, soup):
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
                'origin': 'jobs.github.com',
                'url': '%s%s' % (self.domain, title.attrs['href']),
            })

        raise gen.Return(data)