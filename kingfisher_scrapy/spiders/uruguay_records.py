from kingfisher_scrapy.spiders.uruguay_base import UruguayBase
from kingfisher_scrapy.util import components, handle_http_error


class UruguayRecords(UruguayBase):
    name = 'uruguay_records'
    data_type = 'record_package'
    skip_latest_release_date = 'Already covered by uruguay_releases'

    @handle_http_error
    def parse_list(self, response):
        pattern = 'https://www.comprasestatales.gub.uy/ocds/record/{}'

        titles = response.xpath('//item/title/text()').getall()
        if self.sample:
            titles = [titles[0]]

        for title in titles:
            identifier = title.split(',')[0].split(':')[1]
            yield self.build_request(pattern.format(identifier), formatter=components(-1))
