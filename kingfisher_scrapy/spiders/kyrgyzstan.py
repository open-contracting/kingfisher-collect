import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class Kyrgyzstan(LinksSpider):
    """
    Domain
      Ministry of Finance
    Caveats
      The planning endpoint is not implemented because is not completely in OCDS.
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
    Bulk download documentation
      http://ocds.zakupki.gov.kg/dashboard/weekly and then to 'API & EXPORT'.
      Direct access to http://ocds.zakupki.gov.kg/api-export doesn't work.
    Swagger API documentation
      https://app.swaggerhub.com/apis/DPAteam/export-api-documentation/1.0
    """
    name = 'kyrgyzstan'

    # BaseSpider
    date_format = 'datetime'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        url = 'http://ocds.zakupki.gov.kg/api/tendering'
        if self.from_date:
            from_date = self.from_date.strftime(self.date_format)
            # The API requires the timezone and seconds in the since parameter.
            url = f'{url}?since={from_date}.00%2B06:00'
            self.formatter = staticmethod(parameters('offset', 'since'))
        else:
            from_date = '1970-01-01T00:00:00'
        yield scrapy.Request(url, meta={'file_name': f'{from_date}.json'})
