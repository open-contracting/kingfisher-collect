from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import SimpleSpider


class PeriodicSpider(SimpleSpider):
    """
    This class makes it easy to collect data from an API that accepts a year, a year and month or date ranges
    as parameters.

    #. Inherit from ``PeriodicSpider``
    #. Set a ``date_format`` class attribute to "year", "year-month" or "date".
    #. If ``date_format`` is set to "date", set a ``step`` class attribute to indicate the intervals of days to iterate
       with.
    #. Set a ``pattern`` class attribute to a URL pattern, with placeholders. If the ``date_format`` is "year", then a
       year is passed to the placeholder as an ``int``. If the ``date_format`` is "year-month", then the first day of
       the month is passed to the placeholder as a ``date``, which you can format as, for example:

       .. code-block: python

          pattern = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'

        If the ``date_format`` is "date", then a tuple of dates in intervals of ``step`` days are passed to the
        placeholder.

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

    step = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_requests_callback = getattr(self, self.start_requests_callback)

    def start_requests(self):
        start = self.from_date
        stop = self.until_date
        step = self.step

        if self.date_format == '%Y':
            date_range = util.date_range_by_year(start.year, stop.year)
        elif self.date_format == '%Y-%m':
            date_range = util.date_range_by_month(start, stop)
        else:
            # returns from_date, until_date as a tuple
            date_range = util.date_range_by_interval(start, stop, step)

        for date in date_range:
            urls = self.build_urls(*date) if self.date_format == '%Y-%m-%d' else self.build_urls(date)
            for number, url in enumerate(urls):
                yield self.build_request(url, formatter=self.formatter, callback=self.start_requests_callback,
                                         priority=number * -1)

    def build_urls(self, from_date, until_date=None):
        """
        Yields one or more URLs for the given date.
        """
        yield self.pattern.format(from_date) if not until_date else self.pattern.format(from_date, until_date)
