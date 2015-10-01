from bs4 import BeautifulSoup
from pyjobs.crawlers.spider import BaseSpider


class PyORGCrawlwer(BaseSpider):
    URL = 'https://www.python.org/joddslkjf'
    # URL = 'FLAKSDJFLASJD'

    def parse_response(self, response):
        soup = BeautifulSoup(response.body)
        jobs = soup.find('ol', {'class': 'list-recent-jobs'})
        data = []
        # import ipdb; ipdb.set_trace()

        for node in jobs.findAll('li'):
            title = node.find('span', {'class': 'listing-company-name'})
            title = title.text.split()
            company = title[-1]
            title = ' '.join(title[:-1])
            location = node.find('span', {'class': 'listing-location'}).text
            category = node.find('span', {'class': 'listing-company-category'}).text
            date = node.find('time').attrs['datetime']
            tags = node.find('span', {'class': 'listing-node-type'})
            if tags:
                tags = tags.findAll('a')
                tags = [tag.text for tag in tags]
            else:
                tags = []

            data.append({
                'title': title.strip('New '),
                'company': company,
                'location': location,
                'tags': tags,
                'category': category,
                'date': date,
            })

        return data