from kingfisher_scrapy.spiders.scotland_base import ScotlandBase


class ScotlandProactis(ScotlandBase):
    """
    API documentation
      https://sandbox4.proactislabs.com/v1
    Spider arguments
      sample
        Downloads packages for releases dated one year ago, for each notice type available.
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to one year back.
    """
    name = 'scotland_proactis'
    data_type = 'release_package'

    def start_requests(self):
        from_date = self.from_date if self.from_date else None
        pattern = 'https://sandbox4.proactislabs.com/v1/Notices?dateFrom={}&outputType=0&noticeType={}'
        search_range = 'monthly'
        increment = 1
        return self.parse_requests(pattern, search_range, increment, from_date)
