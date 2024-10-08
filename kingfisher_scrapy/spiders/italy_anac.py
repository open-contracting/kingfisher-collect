import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class ItalyANAC(SimpleSpider):
    """
    Domain
      Autorità Nazionale Anticorruzione (ANAC)
    Caveats
      If the OCID is missing, the spider derives the ``ocid`` field from the ``id`` field.
    API documentation
      https://dati.anticorruzione.it/opendata/about
    Bulk download documentation
      https://dati.anticorruzione.it/opendata/organization/anticorruzione
    """

    name = 'italy_anac'
    download_timeout = 99999

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://dati.anticorruzione.it/opendata/api/3/action/package_search?q=ocds'
        yield scrapy.Request(url, meta={'file_name': 'package_search.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for result in response.json()['result']['results']:
            for resource in result['resources']:
                if resource['format'].upper() == 'JSON':
                    yield self.build_request(resource['url'], formatter=components(-2))

    @handle_http_error
    def parse(self, response):
        data = response.json()
        for release in data['releases']:
            # Kingfisher Process merges only releases with ocids. Extract the ocid from the release id as a fallback.
            # For example: ocds-hu01ve-7608611 from ocds-hu01ve-7608611-01.
            if 'ocid' not in release:
                release['ocid'] = '-'.join(release['id'].split('-')[:3])
        yield self.build_file_from_response(response, data_type=self.data_type, data=data)
