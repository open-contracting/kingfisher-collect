from kingfisher_scrapy.spiders.scotland_base import ScotlandBase


class ScotlandProactis(ScotlandBase):
    """
    API documentation
      https://sandbox4.proactislabs.com/v1
    Spider arguments
      sample
        Downloads packages for releases dated one year ago, for each notice type available.
      from_date
        Download only data from this month onward (MM-YYYY format). Defaults to one year back.
    """
    name = 'scotland_proactis'
    data_type = 'release_package'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ScotlandProactis, cls).from_crawler(crawler, date_format='month', *args, **kwargs)
        return spider

    def start_requests(self):
        from_date = self.from_date if self.from_date else None
        pattern = 'https://sandbox4.proactislabs.com/v1/Notices?dateFrom={}&outputType=0&noticeType={}'
        increment = 1
        return self.parse_requests(pattern, self.date_format, increment, from_date)
