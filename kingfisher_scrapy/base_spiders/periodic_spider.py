from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import SimpleSpider


class PeriodicSpider(SimpleSpider):
    """
    Collect data from an API that accepts a year, year-month, date or datetime as a query string parameter or URL path
    component.

    #. Inherit from ``PeriodicSpider``
    #. Set a ``date_format`` class attribute to "year", "year-month", "date" or "datetime"
    #. Set a ``pattern`` class attribute to a URL pattern, with placeholders. If the ``date_format`` is "year", then a
       year is passed to the placeholder as an ``int``. If the ``date_format`` is "year-month", then the first day of
       the month is passed to the placeholder as a ``date``, which you can format as, for example:

       .. code-block: python

          pattern = 'http://comprasestatales.gub.uy/ocds/rss/{0:%Y}/{0:%m}'

        If the ``date_format`` is "date" or "datetime", then a 2-tuple of ``date`` objects in intervals of ``step``
        days is passed to the placeholder, which you can format as, for example:

       .. code-block: python

          pattern = 'https://api.dgcp.gob.do/api/date/{0:%Y-%m-%d}/{1:%Y-%m-%d}/1'

    #. Set a ``formatter`` class attribute to set the file name like in
       :meth:`~kingfisher_scrapy.base_spiders.BaseSpider.build_request`
    #. Set a ``default_from_date`` class attribute to a year ("YYYY") or year-month ("YYYY-MM")
    #. If the source stopped publishing, set a ``default_until_date`` class attribute to a year or year-month
    #. Optionally, if the ``date_format`` is "date", set a ``step`` class attribute to indicate the length of
       intervals, in days - otherwise, it defaults to 1
    #. Optionally, set a ``start_requests_callback`` class attribute to a method's name as a string - otherwise, it
       defaults to :meth:`~kingfisher_scrapy.base_spiders.simple_spider.SimpleSpider.parse`

    If ``sample`` is set, the data from the most recent year or month is retrieved.
    """

    # PeriodicSpider requires date parameters to be always set.
    date_required = True
    start_requests_callback = "parse"

    # Length of intervals, if `date_format` is "date".
    step = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_requests_callback = getattr(self, self.start_requests_callback)

    def start_requests(self):
        start = self.from_date
        stop = self.until_date

        if self.date_format == "%Y":
            date_range = util.date_range_by_year(start.year, stop.year)
        elif self.date_format == "%Y-%m":
            date_range = util.date_range_by_month(start, stop)
        else:
            date_range = util.date_range_by_interval(start, stop, self.step)

        for date in date_range:
            args = date if self.date_format.startswith("%Y-%m-%d") else [date]
            for number, url in enumerate(self.build_urls(*args)):
                yield self.build_request(
                    url, formatter=self.formatter, callback=self.start_requests_callback, priority=number * -1
                )

    def build_urls(self, from_date, until_date=None):
        """Yield one or more URLs for the given date."""
        if until_date:
            yield self.pattern.format(from_date, until_date)
        else:
            yield self.pattern.format(from_date)
