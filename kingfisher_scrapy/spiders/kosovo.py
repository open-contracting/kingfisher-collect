from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components


class Kosovo(SimpleSpider):
    """
    Domain
      Public Procurement Regulatory Commission
    API documentation
      https://ocdskrpp-test.rks-gov.net/Help
    """
    name = 'kosovo'
    data_type = 'release_list'
    default_from_date = '2000-01-01'

    def start_requests(self):
        stages = ['Award', 'Tender', 'Bid']
        url = 'https://ocdskrpp-test.rks-gov.net/krppAPI/{}'
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

        if self.from_date and self.until_date:
            after = self.until_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            before = self.from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            url = url + '?endDateFrom={}&endDateEnd={}'.format(after, before)

        for stage in stages:
            yield self.build_request(
                url.format(stage, self.from_date, self.until_date),
                headers=headers,
                formatter=components(-1)
            )
