from kingfisher_scrapy.spiders.paraguay_dncp_base import ParaguayDNCPBaseSpider


class ParaguayDNCPReleases(ParaguayDNCPBaseSpider):
    name = 'paraguay_dncp_releases'
    data_type = 'release_package'

    def get_files_to_download(self, content):
        for record in content['records']:
            for release in record['releases']:
                yield release['url']
