import scrapy

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider


class UKContractsFinder(BaseSpider, LinksSpider):
    name = 'uk_fts'

    def start_requests(self):
        yield scrapy.Request(
            url='https://enoticetest.service.xgov.uk/api/1.0/ocdsReleasePackages',
            meta={'kf_filename': 'start.json'},
            headers={'Accept': 'application/json'}
        )

    def parse(self, response):

        if response.status == 200:

            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type='release_package_in_ocdsReleasePackage_in_list_in_results'
            )

            if not self.is_sample():
                yield self.next_link(response)
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
