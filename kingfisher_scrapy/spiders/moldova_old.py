import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


class MoldovaOld(SimpleSpider):
    """
    Bulk download documentation
      http://opencontracting.date.gov.md/downloads
    Spider arguments
      sample
        Download only data released on 2017.
    """
    name = 'moldova_old'
    data_type = 'release_package'

    def start_requests(self):
        if self.sample:
            yield scrapy.Request(
                'http://opencontracting.date.gov.md/ocds-api/year/2017',
                meta={'kf_filename': 'sample.json'}
            )
        else:
            for year in range(2012, 2018):
                yield scrapy.Request(
                    'http://opencontracting.date.gov.md/ocds-api/year/%d' % year,
                    meta={'kf_filename': 'year-%d.json' % year}
                )
