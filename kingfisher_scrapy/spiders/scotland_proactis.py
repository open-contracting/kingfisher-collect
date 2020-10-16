from kingfisher_scrapy.spiders.scotland_base import ScotlandBase


class ScotlandProactis(ScotlandBase):
    """
    API documentation
      https://sandbox4.proactislabs.com/v1
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2019-01'.
    """
    name = 'scotland_proactis'
    data_type = 'release_package'
    pattern = 'https://sandbox4.proactislabs.com/v1/Notices?dateFrom={:%m-%Y}&outputType=0&noticeType={}'
