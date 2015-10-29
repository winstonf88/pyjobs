from tornado import gen

from pyjobs.crawlers.spider import BaseSpider
from pyjobs.utils import URLParser

import logging

logger = logging.getLogger(__name__)


class StackOverflowCrawler(BaseSpider):
    url_parser = URLParser(
        url='http://careers.stackoverflow.com/jobs',
        description='searchTerm'
    )

    @gen.coroutine
    def fetch_links(self, response, soup):
        urls = []
        if 'pg=' not in response.effective_url:
            links = soup.find('div', {'class': 'pagination'})
            if links:
                links = links.findAll('a', {'class': 'job-link'})
                links = links[1:-1]  # ignore current and last
                for link in links:
                    url = '%s%s' % (self.url_root, link.attrs['href'])
                    urls.append(url)
        raise gen.Return(urls)

    @gen.coroutine
    def parse_response(self, response, soup):
        jobs = soup.find('div', {'class': 'listResults'})
        data = []
        
        for node in jobs.findAll('div', {'class': '-job'}):
            title = node.find('a', {'class': 'job-link'})
            url = '%s%s' % (self.url_root, title.attrs['href'])
            company = node.find('strong', {'class': '-employer'}).text
            metadata = node.find('p', {'class': 'location'})
            location = metadata.text.split('\n')[2].strip()
            date = node.find('p', {'class': 'posted'}).text.strip()
            
            tags = node.findAll('a', {'class': 'post-tag'})
            tags = [tag.text for tag in tags]
            tags.extend([tag.text for tag in metadata.findAll('a')])

            data.append({
                'title': title.text.strip(),
                'company': company,
                'location': location,
                'tags': tags,
                'category': '',
                'date': date,
                'origin': self.url_parser.hostname,
                'url': url,
            })

        raise gen.Return(data)
