from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import components, handle_http_error


class UruguayRecords(UruguayBase):
    """
    Domain
      Agencia Reguladora de Compras Estatales (ARCE)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2017-11'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current year-month.
    API documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    """
    name = 'uruguay_records'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # uruguay_releases

    # SimpleSpider
    data_type = 'record_package'

    @handle_http_error
    def parse_list(self, response):
        pattern = 'https://www.comprasestatales.gub.uy/ocds/record/{}'

        titles = response.xpath('//item/title/text()').getall()
        if self.sample:
            titles = [titles[0]]

        for title in titles:
            identifier = title.split(',')[0].split(':')[1]
            yield self.build_request(pattern.format(identifier), formatter=components(-1))
