import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MoldovaOld(BaseSpider):
    name = 'moldova_old'
    custom_settings = {
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        if self.is_sample():
            yield scrapy.Request(
                url='http://opencontracting.date.gov.md/ocds-api/year/2017',
                meta={'kf_filename': 'sample.json'}
            )
        else:
            for year in range(2012, 2018):
                yield scrapy.Request(
                    url='http://opencontracting.date.gov.md/ocds-api/year/%d' % year,
                    meta={'kf_filename': 'year-%d.json' % year}
                )

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type='release_package')
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
