import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters, replace_parameters


class ItalyMinistryOfInfrastructureAndTransport(SimpleSpider):
    """
    Domain
      Public Contracts Service (SCP) - Ministry of Infrastructure and Transport
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2022-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    Swagger API documentation
      https://www.serviziocontrattipubblici.it/ocds-ms/swagger-ui.html
    """

    name = 'italy_ministry_of_infrastructure_and_transport'

    # BaseSpider
    date_format = 'date'
    default_from_date = '2022-01-01'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://www.serviziocontrattipubblici.it/ocdsReleasePackages-ms/v1.0/ocdsReleasePackages?page=1&pageSize=5'
        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            url = f'{url}&dataInvioDa={from_date}&dataInvioA={until_date}'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json', 'page': 1})

    @handle_http_error
    def parse(self, response):
        """
        A success response is returned instead of an error response: for example, for unavailable date periods:

        {
          "esito": false,
          "errorData": "Si è verificato un errore durante la creazione di OCDS"
        }
        """
        data = response.json()

        if 'errorData' in data:
            data['http_code'] = response.status
            yield self.build_file_error_from_response(response, errors=data)

        # An empty release package is returned after the last meaningful page is reached.
        if 'releases' not in data:
            return

        yield from super().parse(response)

        page = response.request.meta['page'] + 1
        yield self.build_request(
            replace_parameters(response.url, page=page), meta={'page': page}, formatter=parameters('page')
        )
