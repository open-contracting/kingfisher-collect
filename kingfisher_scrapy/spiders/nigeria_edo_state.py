import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class NigeriaEdoState(SimpleSpider):
    """
    Domain
      Edo State Open Contracting Data Standards Portal
    Caveats
      The release list has additional numbered keys with tender, award and contract releases as values. This spider
      removes the numbered keys and append the releases into the release list.
    Bulk download documentation
      http://edpms.edostate.gov.ng/ocds/
    """
    name = 'nigeria_edo_state'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'http://edpms.edostate.gov.ng/ocds/bulkjson.php'
        yield scrapy.Request(url, meta={'file_name': 'all.json'})

    @handle_http_error
    def parse(self, response):
        data = response.json()
        # The release list has additional numbered keys with tender, award and contract releases as values, e.g.:
        #
        #   "releases": [
        #     "tender": {
        #       ...
        #     },
        #     "0": {
        #       "ocid": "ocds-fmoaoq-edsg--00546",
        #       "id": "ocds-fmoaoq-edsg--00546-02-tender",
        #     }
        #   ]
        releases = []
        for release in data['releases']:
            for key in list(release):
                if key.isnumeric():
                    # remove the numbered key and append the release into the releases list
                    releases.append(release[key])
                    del release[key]
        data['releases'].extend(releases)
        yield self.build_file_from_response(response, data=data, data_type=self.data_type)
