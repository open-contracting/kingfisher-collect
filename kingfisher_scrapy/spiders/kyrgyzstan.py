import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Kyrgyzstan(LinksSpider):
    """
    Domain
      Ministry of Finance
    Caveats
      The planning endpoint is not implemented because is not completely in OCDS.
    Bulk download documentation
      http://ocds.zakupki.gov.kg/dashboard/weekly and then to 'API & EXPORT'.
      Direct access to http://ocds.zakupki.gov.kg/api-export doesn't work.
    Swagger API documentation
      https://app.swaggerhub.com/apis/DPAteam/export-api-documentation/1.0
    """
    name = 'kyrgyzstan'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        yield scrapy.Request('http://ocds.zakupki.gov.kg/api/tendering', meta={'file_name': 'offset-0.json'})
