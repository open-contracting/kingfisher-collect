import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class MexicoINAIBase(SimpleSpider):
    """
    Collect data from an API that implements the `Mexico INAI Contrataciones Abiertas
    platform <https://github.com/datosabiertosmx/contrataciones-abiertas-infraestructura>`__.

    #. Inherit from ``MexicoINAIBase``
    #. Set a ``base_url`` class attribute with the portal's domain
    #. Set a ``default_from_date`` class attribute with the initial year to scrape when a ``until_date`` argument is
    set

    .. code-block:: python

        from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase

        class MySpider(MexicoINAIBase):
            name = 'my_spider'

            # BaseSpider
            default_from_date = '2020'

            # MexicoINAIBase
            base_url = 'http://base-url'
    """

    # BaseSpider
    root_path = 'arrayReleasePackage.item'
    date_format = 'year'

    # SimpleSpider
    data_type = 'release_package'

    # base_url must be provided by subclasses.

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}/edca/fiscalYears', meta={'file_name': 'list.json'},
                             callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        """
        The response looks like:

        {
          "fiscalYears": [
            {
              "id": "..",
              "year": "..",
              "status": "..",
              "createdAt": "..",
              "updatedAt": "..",
            }
          ]
        }
        """
        for item in response.json()['fiscalYears']:
            year = item['year']
            if self.from_date and self.until_date and not (self.from_date.year <= year <= self.until_date.year):
                continue
            yield self.build_request(f'{self.base_url}/edca/contractingprocess/{year}', formatter=join(components(-1)))
