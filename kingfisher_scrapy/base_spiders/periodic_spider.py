from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import SimpleSpider


class PeriodicSpider(SimpleSpider):
    """
    This class makes it easy to collect data from an API that accepts a year or a year and month as parameters.

    #. Inherit from ``PeriodicSpider``
    #. Set a ``date_format`` class attribute to "year" or "year-month"
    #. Set a ``pattern`` class attribute to a URL pattern, with placeholders. If the ``date_format`` is "year", then a
       year is passed to the placeholder as an ``int``. If the ``date_format`` is "year-month", then the first day of
       the month is passed to the placeholder as a ``date``, which you can format as, for example:

       .. code-block: python

          pattern = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'

    #. Set a ``formatter`` class attribute to set the file name like in
       :meth:`~kingfisher_scrapy.base_spiders.BaseSpider.build_request`
    #. Set a ``default_from_date`` class attribute to a year ("YYYY") or year-month ("YYYY-MM")
    #. If the source stopped publishing, set a ``default_until_date`` class attribute to a year or year-month
    #. Optionally, set a ``start_requests_callback`` class attribute to a method's name as a string - otherwise, it
       defaults to :meth:`~kingfisher_scrapy.base_spiders.simple_spider.SimpleSpider.parse`

    If ``sample`` is set, the data from the most recent year or month is retrieved.
    """

    # PeriodicSpider requires date parameters to be always set.
    date_required = True
    start_requests_callback = 'parse'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_requests_callback = getattr(self, self.start_requests_callback)

    def start_requests(self):
        start = self.from_date
        stop = self.until_date

        if self.date_format == '%Y':
            date_range = util.date_range_by_year(start.year, stop.year)
        else:
            date_range = util.date_range_by_month(start, stop)

        for date in date_range:
            for number, url in enumerate(self.build_urls(date)):
                yield self.build_request(url, formatter=self.formatter, callback=self.start_requests_callback,
                                         priority=number * -1)

    def build_urls(self, date):
        """
        Yields one or more URLs for the given date.
        """
        yield self.pattern.format(date)
