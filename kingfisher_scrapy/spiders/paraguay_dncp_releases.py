from kingfisher_scrapy.spiders.paraguay_base import ParaguayDNCPBaseSpider
from urllib.parse import urlparse

class ParaguayDNCPReleases(ParaguayDNCPBaseSpider):
    name = 'paraguay_dncp_releases'
    data_type = 'release_package'

    def get_files_to_download(self, content):
        for record in content['records']:
            for release in record['releases']:
                parsed = urlparse(release['url'])
                path = parsed.path.lstrip("/datos/api/v3/doc/")
                id = path.lstrip("releases")
                if id:
                    url = 'http://beta.dncp.gov.py/datos/api/v3/doc/ocds/releases/id{}'.format(id)
                    yield url
                else:
                    raise Exception('Release ID not found')
