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
    date_format = 'datetime'
    default_from_date = '2000-01-01T00:00:00'

    def start_requests(self):
        stages = ['Award', 'Tender', 'Bid']
        url = 'https://ocdskrpp-test.rks-gov.net/krppAPI/{}'
        headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            url = f'{url}?endDateFrom={from_date}&endDateEnd={until_date}'

        for stage in stages:
            yield self.build_request(
                url.format(stage),
                headers=headers,
                formatter=components(-1)
            )
