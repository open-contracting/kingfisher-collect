from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error


class HondurasSEFINAPI(PeriodicSpider):
    """
    Domain
      Secretaria de Finanzas de Honduras (SEFIN)
    Caveats
     The API returns HTTP 500 error for the data between 2012 and 2018,
     however, these datasets are available in the bulk download method.
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2019'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://www.sefin.gob.hn/edca/
    Swagger API documentation
      https://guancasco.sefin.gob.hn/EDCA_WEBAPI/swagger/ui/index
    """
    name = 'honduras_sefin_api'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2019'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'https://guancasco.sefin.gob.hn/EDCA_WEBAPI/api/listaOcids/{}'
    formatter = staticmethod(components(-1))  # year

    @handle_http_error
    def parse(self, response):
        data = response.json()
        for url in data:
            # URL looks like https://guancasco.sefin.gob.hn/EDCA_WEBAPI/api/releasePackage/P2022-3-1-197
            yield self.build_request(url, formatter=self.formatter, callback=super().parse)
