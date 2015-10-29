from tornado import gen

from pyjobs.crawlers.spider import BaseSpider
from pyjobs.utils import URLParser

import logging

logger = logging.getLogger(__name__)


class PyORGCrawler(BaseSpider):
    url_parser = URLParser(
        url='https://www.python.org/jobs',
        description=None,
        location=None
    )

    @gen.coroutine
    def fetch_links(self, response, soup):
        """Fetch next pages."""
        urls = []
        if '?page' not in response.effective_url:
            pagination = soup.find('ul', {'class': 'pagination menu'})
            pages = pagination.findAll('a')[1:-1]
            for page in pages:
                url = '%s%s' % (self.base_url, page.attrs['href'])
                urls.append(url)
        raise gen.Return(urls)

    @gen.coroutine
    def parse_response(self, response, soup):
        """Extract job info from response."""
        jobs = soup.find('ol', {'class': 'list-recent-jobs'})
        data = []

        for node in jobs.findAll('li'):
            title = node.find('span', {'class': 'listing-company-name'})
            url = '%s%s' % (self.url_root, title.find('a').attrs['href'])
            title = title.text.split('\t')
            company = ' '.join(title[1:]).strip()
            title = title[0].strip()

            location = node.find('span', {'class': 'listing-location'}).text
            category = node.find('span', {'class': 'listing-company-category'}).text
            date = node.find('time').attrs['datetime']
            tags = node.find('span', {'class': 'listing-job-type'})
            if tags:
                tags = [tag.text for tag in tags.findAll('a')]
            else:
                tags = []

            data.append({
                'title': title.strip('New '),
                'company': company,
                'location': location,
                'tags': tags,
                'category': category,
                'date': date,
                'origin': self.url_parser.hostname,
                'url': url,
            })

        raise gen.Return(data)
