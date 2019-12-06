import re

from kingfisher_scrapy.spiders.paraguay_base import ParaguayDNCPBaseSpider


class ParaguayDNCPReleases(ParaguayDNCPBaseSpider):
    name = 'paraguay_dncp_releases'
    data_type = 'release_package'

    def get_files_to_download(self, content):
        for record in content['records']:
            for release in record['releases']:
                match = re.search('[^/]+$', release['url'])
                if match:
                    url = 'http://beta.dncp.gov.py/datos/api/v3/doc/ocds/releases/id/{}'.format(match.group(0))
                    file_name = '{}.json'.format(match.group(0))
                    yield url, file_name
                else:
                    raise Exception('Release ID not found')
