import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class UKFTS(LinksSpider):
    """
    Domain
      Find a Tender Service (FTS)
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
        If ``until_date`` is provided, defaults to '2021-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format).
        If ``from_date`` is provided, defaults to now.
    API documentation
      https://www.find-tender.service.gov.uk/apidocumentation/1.0/GET-ocdsReleasePackages
    """
    name = 'uk_fts'

    # BaseSpider
    date_format = 'datetime'
    default_from_date = '2021-01-01T00:00:00'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('cursor'))

    def start_requests(self):
        url = 'https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages'
        if self.from_date and self.until_date:
            self.from_date = self.from_date.strftime(self.date_format)
            self.until_date = self.until_date.strftime(self.date_format)
            url = f'{url}?updatedFrom={self.from_date}&updatedTo={self.until_date}'

        yield scrapy.Request(url, meta={'file_name': 'start.json'}, headers={'Accept': 'application/json'})

    @handle_http_error
    def parse(self, response):
        data = response.text
        # TODO: temporary fix for https://github.com/open-contracting/kingfisher-process/issues/323, remove when it's
        #  solved in kingfisher process
        data = data.replace('1e9999', '9999999')
        response = response.replace(body=data)
        yield from super().parse(response)
