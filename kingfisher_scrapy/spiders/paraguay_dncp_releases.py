from kingfisher_scrapy.spiders.paraguay_base import ParaguayDNCPBaseSpider
from urllib.parse import urlparse


class ParaguayDNCPReleases(ParaguayDNCPBaseSpider):
    name = 'paraguay_dncp_releases'
    data_type = 'release_package'

    def get_files_to_download(self, content):
        for record in content['records']:
            for release in record['releases']:
                parsed = urlparse(release['url'])
                id_path = parsed.path.replace("/datos/api/v3/doc/releases/", "")
                if id_path:
                    url = 'http://beta.dncp.gov.py/datos/api/v3/doc/ocds/releases/id/{}'.format(id_path)
                    yield url
                else:
                    raise Exception('Release ID not found')
