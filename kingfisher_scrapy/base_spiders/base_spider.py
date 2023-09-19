import codecs
from datetime import datetime

import scrapy

from kingfisher_scrapy.exceptions import IncoherentConfigurationError, SpiderArgumentError
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.util import add_path_components, add_query_string


class BaseSpider(scrapy.Spider):
    """
    With respect to the data's source:

    -  If the source can support ``from_date`` and ``until_date`` spider arguments:

       -  Set a ``date_format`` class attribute to "date", "datetime", "year" or "year-month" (default "date").
       -  Set a ``default_from_date`` class attribute to a date ("YYYY-MM-DD"), datetime ("YYYY-MM-DDTHH:MM:SS"),
          year ("YYYY") or year-month ("YYYY-MM").
       -  If the source stopped publishing, set a ``default_until_date`` class attribute to a date or datetime.

    -  If the spider requires date parameters to be set, add a ``date_required = True`` class attribute, and set the
       ``date_format`` and ``default_from_date`` class attributes as above.
    -  If the spider needs to parse the JSON response in its ``parse`` method, set ``dont_truncate = True``.

    .. tip::

        If ``date_required`` is ``True``, or if either the ``from_date`` or ``until_date`` spider arguments are set,
        then ``from_date`` defaults to the ``default_from_date`` class attribute, and ``until_date`` defaults to the
        ``get_default_until_date()`` return value (which is the current time, by default).

    With respect to the data's format:

    -  If the data is not encoded using UTF-8, set an ``encoding`` class attribute to its encoding.
    -  If the data is a concatenated JSON, add a ``concatenated_json = True`` class attribute.
    -  If the data is line-delimited JSON, add a ``line_delimited = True`` class attribute.
    -  If the data embeds OCDS data within other objects or arrays, set a ``root_path`` class attribute to the path to
       the OCDS data, e.g. ``'releasePackage'`` or ``'results.item'``.
    -  If the data is in CSV or XLSX format, add a ``unflatten = True`` class attribute to convert it to JSON using
       Flatten Tool's ``unflatten`` function. To pass arguments to ``unflatten``, set a ``unflatten_args`` dict.
    -  If the data source uses OCDS 1.0, add an ``ocds_version = '1.0'`` class attribute. This is used for the
       :ref:`Kingfisher Process<kingfisher-process>` extension.

    With respect to support for Kingfisher Collect's features:

    -  If the spider doesn't work with the ``pluck`` command, set a ``skip_pluck`` class attribute to the reason.
    """
    VALID_DATE_FORMATS = {'date': '%Y-%m-%d', 'datetime': '%Y-%m-%dT%H:%M:%S', 'year': '%Y', 'year-month': '%Y-%m'}

    # Regarding the data source.
    date_format = 'date'
    date_required = False
    dont_truncate = False

    # Regarding the data format.
    encoding = 'utf-8'
    concatenated_json = False
    line_delimited = False
    root_path = ''
    unflatten = False
    unflatten_args = {}
    ocds_version = '1.1'

    # Regarding the access method.
    max_attempts = 1
    retry_http_codes = []

    # Not to be overridden by sub-classes.
    available_steps = {'compile', 'check'}

    def __init__(self, sample=None, path=None, from_date=None, until_date=None, crawl_time=None, note=None,
                 keep_collection_open=None, steps=None, compile_releases=None, table_name=None, package_pointer=None,
                 release_pointer=None, truncate=None, *args, **kwargs):
        """
        :param sample: the number of items to download (``'true'`` means ``1``; ``'false'`` and ``None`` mean no limit)
        :param path: path components to append to the URLs yielded by the ``start_requests`` method (see :ref:`filter`)
        :param from_date: the date from which to download data (see :ref:`spider-arguments`)
        :param until_date: the date until which to download data (see :ref:`spider-arguments`)
        :param crawl_time: override the crawl's start time (see :ref:`increment`)
        :param note: a note to add to the collection in Kingfisher Process
        :param keep_collection_open: whether to close the collection in Kingfisher Process when the crawl is finished
        :param compile_releases: whether to create compiled releases from individual releases when using the
                                 :class:`~kingfisher_scrapy.extensions.DatabaseStore` extension
        :param package_pointer: the JSON Pointer to the value in the package (see the :ref:`pluck` command)
        :param release_pointer: the JSON Pointer to the value in the release (see the :ref:`pluck` command)
        :param truncate: the number of characters to which the value is truncated (see the :ref:`pluck` command)
        :param table_name: override the crawl's table name in the database (see :ref:`database_store`)
        """

        super().__init__(*args, **kwargs)

        if self.concatenated_json and self.line_delimited:
            raise IncoherentConfigurationError('concatenated_json = True is incompatible with line_delimited = True.')

        # https://docs.scrapy.org/en/latest/topics/spiders.html#spider-arguments

        # Related to filtering data from the source.
        if sample == 'true':
            self.sample = 1
        elif sample == 'false':
            self.sample = None
        else:
            self.sample = sample
        self.from_date = from_date
        self.until_date = until_date

        # Related to incremental crawls (whether KingfisherProcessAPI2 data_version or DatabaseStore directory).
        self.crawl_time = crawl_time

        # KingfisherProcessAPI2 extension.
        self.kingfisher_process_note = note
        self.kingfisher_process_keep_collection_open = keep_collection_open == 'true'
        if steps is None:
            self.kingfisher_process_steps = self.available_steps
        else:
            self.kingfisher_process_steps = set(steps.split(',')) & self.available_steps

        # DatabaseStore extension.
        self.database_store_compile_releases = compile_releases == 'true'
        self.database_store_table_name = table_name

        # Pluck pipeline.
        self.pluck_package_pointer = package_pointer
        self.pluck_release_pointer = release_pointer
        self.pluck_truncate = int(truncate) if truncate else None
        self.pluck = bool(package_pointer or release_pointer)

        self.query_string_parameters = {}
        for key, value in kwargs.items():
            if key.startswith('qs:'):
                self.query_string_parameters[key[3:]] = value

        self.date_format = self.VALID_DATE_FORMATS[self.date_format]

        if hasattr(self, 'start_requests'):
            if path:
                self.start_requests = add_path_components(self.start_requests, path)
            if self.query_string_parameters:
                self.start_requests = add_query_string(self.start_requests, self.query_string_parameters)

        self.filter_arguments = {
            'from_date': from_date,
            'until_date': until_date,
            'path': path,
        }
        self.filter_arguments.update(kwargs)

        spider_arguments = {
            'sample': sample,
            'note': note,
            'from_date': from_date,
            'until_date': until_date,
            'crawl_time': crawl_time,
            'keep_collection_open': keep_collection_open,
            'package_pointer': package_pointer,
            'release_pointer': release_pointer,
            'truncate': truncate,
            'compile_releases': compile_releases,
        }
        spider_arguments.update(kwargs)

        self.logger.info('Spider arguments: %r', spider_arguments)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        if spider.pluck_package_pointer and spider.pluck_release_pointer:
            raise SpiderArgumentError('You cannot specify both package_pointer and release_pointer spider arguments.')

        if spider.sample:
            try:
                spider.sample = int(spider.sample)
            except ValueError:
                raise SpiderArgumentError(f'spider argument `sample`: invalid integer value: {spider.sample!r}')

        if spider.crawl_time:
            try:
                spider.crawl_time = datetime.strptime(spider.crawl_time, '%Y-%m-%dT%H:%M:%S')
            except ValueError as e:
                raise SpiderArgumentError(f'spider argument `crawl_time`: invalid date value: {e}')

        if spider.from_date or spider.until_date or spider.date_required:
            if not spider.from_date:
                spider.from_date = spider.default_from_date
            try:
                if isinstance(spider.from_date, str):
                    spider.from_date = datetime.strptime(spider.from_date, spider.date_format)
            except ValueError as e:
                raise SpiderArgumentError(f'spider argument `from_date`: invalid date value: {e}')

            if not spider.until_date:
                spider.until_date = cls.get_default_until_date(spider)
            try:
                if isinstance(spider.until_date, str):
                    spider.until_date = datetime.strptime(spider.until_date, spider.date_format)
            except ValueError as e:
                raise SpiderArgumentError(f'spider argument `until_date`: invalid date value: {e}')

        # DatabaseStore-related logic.
        if crawler.settings['DATABASE_URL']:
            if not spider.crawl_time:
                raise SpiderArgumentError("spider argument `crawl_time`: can't be blank if `DATABASE_URL` is set")

        return spider

    def is_http_success(self, response):
        """
        Returns whether the response's status is a non-2xx code.
        """
        # All 2xx codes are successful.
        # https://tools.ietf.org/html/rfc7231#section-6.3
        return 200 <= response.status < 300

    def is_http_retryable(self, response):
        """
        Returns whether the response's status is retryable.

        Set the ``retry_http_codes`` class attribute to a list of status codes to retry.
        """
        return response.status in self.retry_http_codes

    def get_start_time(self, format):
        """
        Returns the formatted start time of the crawl.
        """
        if self.crawl_time:
            date = self.crawl_time
        else:
            date = self.crawler.stats.get_value('start_time')
        return date.strftime(format)

    def get_retry_wait_time(self, response):
        """
        Returns the number of seconds to wait before retrying a URL.
        """
        return int(response.headers['Retry-After'])

    def build_request(self, url, formatter, **kwargs):
        """
        Returns a Scrapy request, with a file name added to the request's ``meta`` attribute. If the file name doesn't
        have a ``.json``, ``.csv``, ``.xlsx``, ``.rar`` or ``.zip`` extension, it adds a ``.json`` extension.

        If the last component of a URL's path is unique, use it as the file name. For example:

        >>> from kingfisher_scrapy.base_spiders import BaseSpider
        >>> from kingfisher_scrapy.util import components
        >>> url = 'https://example.com/package.json'
        >>> formatter = components(-1)
        >>> BaseSpider(name='my_spider').build_request(url, formatter=formatter).meta
        {'file_name': 'package.json'}

        To use a query string parameter as the file name:

        >>> from kingfisher_scrapy.util import parameters
        >>> url = 'https://example.com/packages?page=1&per_page=100'
        >>> formatter = parameters('page')
        >>> BaseSpider(name='my_spider').build_request(url, formatter=formatter).meta
        {'file_name': 'page-1.json'}

        To use a URL path component *and* a query string parameter as the file name:

        >>> from kingfisher_scrapy.util import join
        >>> url = 'https://example.com/packages?page=1&per_page=100'
        >>> formatter = join(components(-1), parameters('page'))
        >>> BaseSpider(name='my_spider').build_request(url, formatter=formatter).meta
        {'file_name': 'packages-page-1.json'}

        :param str url: the URL to request
        :param formatter: a function that accepts a URL and returns a file name
        :returns: a Scrapy request
        :rtype: scrapy.Request
        """
        file_name = formatter(url)
        if not file_name.endswith(('.json', '.csv', '.xlsx', '.rar', '.zip')):
            file_name += '.json'
        meta = {'file_name': file_name}
        if 'meta' in kwargs:
            meta.update(kwargs.pop('meta'))
        return scrapy.Request(url, meta=meta, **kwargs)

    def build_file_from_response(self, response, **kwargs):
        """
        Returns a File item to yield, based on the response to a request.

        If the response body starts with a byte-order mark, it is removed.
        """
        kwargs.setdefault('file_name', response.request.meta['file_name'])
        kwargs.setdefault('url', response.request.url)
        if 'data' not in kwargs:
            body = response.body
            # https://tools.ietf.org/html/rfc7159#section-8.1
            # bytes instances don't have a removeprefix method.
            if body.startswith(codecs.BOM_UTF8):
                body = body[len(codecs.BOM_UTF8):]
            kwargs['data'] = body
        return self.build_file(**kwargs)

    def build_file(self, *, file_name=None, url=None, data=None, data_type=None):
        """
        Returns a File item to yield.
        """
        return File({
            'file_name': file_name,
            'data': data,
            'data_type': data_type,
            'url': url,
        })

    def build_file_item(self, number, data, item):
        """
        Returns a FileItem item to yield.
        """
        return FileItem({
            'number': number,
            'file_name': item['file_name'],
            'data': data,
            'data_type': item['data_type'],
            'url': item['url'],
        })

    def build_file_error_from_response(self, response, **kwargs):
        """
        Returns a FileError item to yield, based on the response to a request.
        """
        item = FileError({
            'url': response.request.url,
            'errors': {'http_code': response.status},
        })
        if 'file_name' in response.request.meta:
            item['file_name'] = response.request.meta['file_name']
        item.update(kwargs)
        return item

    @classmethod
    def get_default_until_date(cls, spider):
        """
        Returns the ``default_until_date`` class attribute if truthy. Otherwise, returns the current time.
        """
        if getattr(spider, 'default_until_date', None):
            return spider.default_until_date
        return datetime.utcnow()
