import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class IndiaCivicDataLab(SimpleSpider):
    """
    Domain
      CivicDataLab
    Bulk download documentation
      https://github.com/CivicDataLab/himachal-pradesh-health-procurement-OCDS/
    """
    name = 'india_civic_data_lab'

    # BaseSpider
    unflatten = True
    unflatten_args = {
        'metatab_name': 'Meta',
        'metatab_vertical_orientation': True
    }

    # SimpleSpider
    data_type = 'release_package'

    # GitHub repository
    github_repo = 'CivicDataLab/himachal-pradesh-health-procurement-OCDS'

    def start_requests(self):
        url = f'https://api.github.com/repos/{self.github_repo}/git/trees/master'
        yield scrapy.Request(url, meta={'file_name': 'response.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        # The parser uses the GitHub API to list the files from the repository and
        # then downloads them with a non-API url to avoid quota/rate limitations

        data = response.json()
        # GitHub Tree API documentation
        # https://docs.github.com/en/rest/reference/git#get-a-tree

        # If truncated is true in the response then the repository has exceeded
        # the maximum number of items can GitHub Tree API do handle
        if data['truncated']:
            self.logger.error('Truncated results in GitHub Tree API request.')
            raise Exception()

        for node in data['tree']:
            file_name = node['path']
            if file_name.endswith('.xlsx'):
                url = f'https://github.com/{self.github_repo}/raw/master/{file_name}?raw=true'
                yield scrapy.Request(url, meta={'file_name': file_name})
