import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MoldovaOld(BaseSpider):
    name = 'moldova_old'

    def start_requests(self):
        if self.sample:
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
            yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                                data_type='release_package')
        else:
            yield self.build_file_error_from_response(response)
