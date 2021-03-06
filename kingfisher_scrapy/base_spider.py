import json
import os
from abc import abstractmethod
from datetime import datetime
from io import BytesIO
from math import ceil
from zipfile import ZipFile

import ijson
import scrapy
from jsonpointer import resolve_pointer
from rarfile import RarFile

from kingfisher_scrapy import util
from kingfisher_scrapy.exceptions import MissingNextLinkError, SpiderArgumentError
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.util import add_query_string, handle_http_error

browser_user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'  # noqa: E501


class BaseSpider(scrapy.Spider):
    """
    -  If the data source uses OCDS 1.0, add an ``ocds_version = '1.0'`` class attribute. This is used for `Kingfisher
       Process integration <https://github.com/open-contracting/kingfisher-collect/issues/411>`__.
    -  If the spider supports ``from_date`` and ``until_date`` spider arguments, set the ``default_from_date`` class
       attribute to a date string.
    -  If a spider requires date parameters to be set, add a ``date_required = True`` class attribute, and set the
       ``default_from_date`` class attribute to a date string.
    -  If the spider doesn't work with the ``pluck`` command, set a ``skip_pluck`` class attribute to the reason.
    -  If a spider collects data as CSV or XLSX files, set the class attribute ``unflatten = True`` to convert each
       item to json files in the Unflatten pipeline class using the ``unflatten`` command from Flatten Tool.
       If you need to set more arguments for the unflatten command, set a ``unflatten_args`` dict with them.
    If ``date_required`` is ``True``, or if either the ``from_date`` or ``until_date`` spider arguments are set, then
    ``from_date`` defaults to the ``default_from_date`` class attribute, and ``until_date`` defaults to the
    ``get_default_until_date()`` return value (which is the current time, by default).
    """
    MAX_RELEASES_PER_PACKAGE = 100
    VALID_DATE_FORMATS = {'date': '%Y-%m-%d', 'datetime': '%Y-%m-%dT%H:%M:%S'}

    ocds_version = '1.1'
    date_format = 'date'
    date_required = False
    unflatten = False
    unflatten_args = {}

    def __init__(self, sample=None, note=None, from_date=None, until_date=None, crawl_time=None,
                 keep_collection_open=None, package_pointer=None, release_pointer=None, truncate=None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # https://docs.scrapy.org/en/latest/topics/spiders.html#spider-arguments
        if sample == 'true' or sample is True:
            self.sample = 1
        elif sample == 'false' or sample is False:
            self.sample = None
        else:
            self.sample = sample
        self.note = note
        self.from_date = from_date
        self.until_date = until_date
        self.crawl_time = crawl_time
        self.keep_collection_open = keep_collection_open == 'true'
        # Pluck-related arguments.
        self.package_pointer = package_pointer
        self.release_pointer = release_pointer
        self.truncate = int(truncate) if truncate else None

        self.query_string_parameters = {}
        for key, value in kwargs.items():
            if key.startswith('qs:'):
                self.query_string_parameters[key[3:]] = value

        self.date_format = self.VALID_DATE_FORMATS[self.date_format]
        self.pluck = bool(package_pointer or release_pointer)

        if self.query_string_parameters and hasattr(self, 'start_requests'):
            self.start_requests = add_query_string(self.start_requests, self.query_string_parameters)

        self.filter_arguments = {
            'from_date': from_date,
            'until_date': until_date,
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
        }
        spider_arguments.update(kwargs)
        self.logger.info('Spider arguments: %r', spider_arguments)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        if spider.package_pointer and spider.release_pointer:
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

        return spider

    def is_http_success(self, response):
        """
        Returns whether the response status is a non-2xx code.
        """
        # All 2xx codes are successful.
        # https://tools.ietf.org/html/rfc7231#section-6.3
        return 200 <= response.status < 300

    def get_start_time(self, format):
        """
        Returns the formatted start time of the crawl.
        """
        if self.crawl_time:
            date = self.crawl_time
        else:
            date = self.crawler.stats.get_value('start_time')
        return date.strftime(format)

    def build_request(self, url, formatter, **kwargs):
        """
        Returns a Scrapy request, with a file name added to the request's ``meta`` attribute. If the file name doesn't
        have a ``.json`` or ``.zip`` extension, it adds a ``.json`` extension.

        If the last component of a URL's path is unique, use it as the file name. For example:

        >>> from kingfisher_scrapy.base_spider import BaseSpider
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
        if not file_name.endswith(('.json', '.zip', '.xlsx', '.csv', '.rar')):
            file_name += '.json'
        meta = {'file_name': file_name}
        if 'meta' in kwargs:
            meta.update(kwargs.pop('meta'))
        return scrapy.Request(url, meta=meta, **kwargs)

    def build_file_from_response(self, response, **kwargs):
        """
        Returns a File item to yield, based on the response to a request.
        """
        kwargs.setdefault('file_name', response.request.meta['file_name'])
        kwargs.setdefault('url', response.request.url)
        kwargs.setdefault('data', response.body)
        return self.build_file(**kwargs)

    def build_file(self, *, file_name=None, url=None, data=None, data_type=None, encoding='utf-8', post_to_api=True):
        """
        Returns a File item to yield.
        """
        return File({
            'file_name': file_name,
            'data': data,
            'data_type': data_type,
            'url': url,
            'encoding': encoding,
            'post_to_api': post_to_api,
        })

    def build_file_item(self, *, number=None, file_name=None, url=None, data=None, data_type=None, encoding='utf-8'):
        """
        Returns a FileItem item to yield.
        """
        return FileItem({
            'number': number,
            'file_name': file_name,
            'data': data,
            'data_type': data_type,
            'url': url,
            'encoding': encoding,
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

    def _get_package_metadata(self, f, skip_key):
        """
        Returns the package metadata from a file object.

        :param f: a file object
        :param str skip_key: the key to skip
        :returns: the package metadata
        :rtype: dict
        """
        package = {}
        for item in util.items(ijson.parse(f), '', skip_key=skip_key):
            package.update(item)
        return package

    def parse_json_lines(self, f, *, file_name='data.json', url=None, data_type=None, encoding='utf-8'):
        for number, line in enumerate(f, 1):
            if self.sample and number > self.sample:
                break
            if isinstance(line, bytes):
                line = line.decode(encoding=encoding)
            yield self.build_file_item(number=number, file_name=file_name, url=url, data=line, data_type=data_type,
                                       encoding=encoding)

    def parse_json_array(self, f_package, f_list, *, file_name='data.json', url=None, data_type=None, encoding='utf-8',
                         array_field_name='releases'):
        if self.sample:
            size = self.sample
        else:
            size = self.MAX_RELEASES_PER_PACKAGE

        package = self._get_package_metadata(f_package, array_field_name)

        for number, items in enumerate(util.grouper(ijson.items(f_list, f'{array_field_name}.item'), size), 1):
            package[array_field_name] = filter(None, items)
            data = json.dumps(package, default=util.default)
            yield self.build_file_item(number=number, file_name=file_name, url=url, data=data, data_type=data_type,
                                       encoding=encoding)
            if self.sample:
                break

    @classmethod
    def get_default_until_date(cls, spider):
        """
        Returns the default value of the ``until_date`` spider argument.
        """
        return datetime.utcnow()


class SimpleSpider(BaseSpider):
    """
    Most spiders can inherit from this class. It assumes all responses have the same data type.

    #. Inherit from ``SimpleSpider``
    #. Set a ``data_type`` class attribute to the data type of the responses
    #. Optionally, set an ``encoding`` class attribute to the encoding of the responses (default UTF-8)
    #. Optionally, set a ``data_pointer`` class attribute to the JSON Pointer for OCDS data (default "")
    #. Write a ``start_requests`` method (and any intermediate callbacks) to send requests

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spider import SimpleSpider

        class MySpider(SimpleSpider):
            name = 'my_spider'
            data_type = 'release_package'

            def start_requests(self):
                yield scrapy.Request('https://example.com/api/package.json', meta={'file_name': 'all.json'})
    """

    encoding = 'utf-8'
    data_pointer = ''

    @handle_http_error
    def parse(self, response):
        kwargs = {}
        if self.data_pointer:
            kwargs['data'] = json.dumps(resolve_pointer(response.json(), self.data_pointer)).encode()

        yield self.build_file_from_response(response, data_type=self.data_type, encoding=self.encoding, **kwargs)


class CompressedFileSpider(BaseSpider):
    """
    This class makes it easy to collect data from ZIP or RAR files. It assumes all files have the same data type.

    #. Inherit from ``CompressedFileSpider``
    #. Set a ``data_type`` class attribute to the data type of the compressed files
    #. Optionally, set an ``encoding`` class attribute to the encoding of the compressed files (default UTF-8)
    #. Optionally, set a ``compressed_file_format`` class attribute to the format of the compressed files

       ``json_lines``
         Yields each line of each compressed file.
         The archive file is saved to disk. The compressed files are *not* saved to disk.
       ``release_package``
         Re-packages the releases in the compressed files in groups of
         :const:`~kingfisher_scrapy.base_spider.BaseSpider.MAX_RELEASES_PER_PACKAGE`, and yields the packages.
         The archive file is saved to disk. The compressed files are *not* saved to disk.
       ``None``
         Yields each compressed file.
         Each compressed file is saved to disk. The archive file is *not* saved to disk.

    #. Write a ``start_requests`` method to request the archive files

    .. code-block:: python

        from kingfisher_scrapy.base_spider import CompressedFileSpider
        from kingfisher_scrapy.util import components

        class MySpider(CompressedFileSpider):
            name = 'my_spider'
            data_type = 'release_package'

            def start_requests(self):
                yield self.build_request('https://example.com/api/packages.zip', formatter=components(-1))
    """

    encoding = 'utf-8'
    skip_pluck = 'Archive files are not supported'
    compressed_file_format = None
    file_name_must_contain = ''

    @handle_http_error
    def parse(self, response):
        archive_name, archive_format = os.path.splitext(response.request.meta['file_name'])
        archive_format = archive_format[1:].lower()
        if self.compressed_file_format:
            yield self.build_file_from_response(response, data_type=archive_format, post_to_api=False)
        if archive_format == 'zip':
            cls = ZipFile
        else:
            cls = RarFile
        archive_file = cls(BytesIO(response.body))
        for file_info in archive_file.infolist():
            filename = file_info.filename
            basename = os.path.basename(filename)
            if self.file_name_must_contain not in basename:
                continue
            if archive_format == 'rar' and file_info.isdir():
                continue
            if archive_format == 'zip' and file_info.is_dir():
                continue
            if not basename.endswith('.json'):
                basename += '.json'

            data = archive_file.open(filename)

            kwargs = {
                'file_name': basename,
                'url': response.request.url,
                'data_type': self.data_type,
                'encoding': self.encoding,
            }
            if self.compressed_file_format == 'json_lines':
                yield from self.parse_json_lines(data, **kwargs)
            elif self.compressed_file_format == 'release_package':
                package = archive_file.open(filename)
                yield from self.parse_json_array(package, data, **kwargs)
            else:
                yield self.build_file(data=data.read(), **kwargs)


class LinksSpider(SimpleSpider):
    """
    This class makes it easy to collect data from an API that implements the `pagination
    <https://github.com/open-contracting-extensions/ocds_pagination_extension>`__ pattern:

    #. Inherit from ``LinksSpider``
    #. Set a ``data_type`` class attribute to the data type of the API responses
    #. Set a ``next_page_formatter`` class attribute to set the file name as in
       :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_request`
    #. Write a ``start_requests`` method to request the first page of API results
    #. Optionally, set a ``next_pointer`` class attribute to the JSON Pointer for the next link (default "/links/next")

    If the API returns the number of total pages or results in the response, consider using ``IndexSpider`` instead.

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spider import LinksSpider

        class MySpider(LinksSpider):
            name = 'my_spider'
            data_type = 'release_package'

            def start_requests(self):
                yield scrapy.Request('https://example.com/api/packages.json', meta={'file_name': 'page1.json'})

    """

    next_pointer = '/links/next'

    @handle_http_error
    def parse(self, response):
        yield from super().parse(response)

        yield self.next_link(response)

    def next_link(self, response, **kwargs):
        """
        If the JSON response has a ``links.next`` key, returns a ``scrapy.Request`` for the URL.
        """
        data = response.json()
        url = resolve_pointer(data, self.next_pointer, None)
        if url:
            return self.build_request(url, formatter=self.next_page_formatter, **kwargs)

        for filter_argument in self.filter_arguments:
            if getattr(self, filter_argument, None):
                return

        if response.meta['depth'] == 0:
            raise MissingNextLinkError(f'next link not found on the first page: {response.url}')


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

    #. Implement a ``get_formatter`` method to return the formatter to use in
       :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_request` calls
    #. Set a ``default_from_date`` class attribute to a year ("YYYY") or year-month ("YYYY-MM") as a string
    #. Optionally, set a ``default_until_date`` class attribute to a year ("YYYY") or year-month ("YYYY-MM") as a
       string, if the source is known to have stopped publishing - otherwise, it defaults to today
    #. Optionally, set a ``start_requests_callback`` class attribute to a method's name - otherwise, it defaults to
       :meth:`~kingfisher_scrapy.base_spider.SimpleSpider.parse`

    If ``sample`` is set, the data from the most recent year or month is retrieved.
    """
    VALID_DATE_FORMATS = {'year': '%Y', 'year-month': '%Y-%m'}

    # PeriodicSpider requires date parameters to be always set.
    date_required = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if hasattr(self, 'start_requests_callback'):
            self.start_requests_callback = getattr(self, self.start_requests_callback)
        else:
            self.start_requests_callback = self.parse

    @classmethod
    def get_default_until_date(cls, spider):
        """
        Returns the ``default_until_date`` class attribute if truthy. Otherwise, returns today's date.
        """
        if getattr(spider, 'default_until_date', None):
            return spider.default_until_date
        return datetime.today()

    def start_requests(self):
        start = self.from_date
        stop = self.until_date

        if self.date_format == '%Y':
            date_range = util.date_range_by_year(start.year, stop.year)
        else:
            date_range = util.date_range_by_month(start, stop)

        for date in date_range:
            for url in self.build_urls(date):
                yield self.build_request(url, self.get_formatter(), callback=self.start_requests_callback)

    def build_urls(self, date):
        """
        Yields one or more URLs for the given date.
        """
        yield self.pattern.format(date)

    @abstractmethod
    def get_formatter(self):
        """
        Returns the formatter to use in :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_request` calls.
        """
        pass


class IndexSpider(SimpleSpider):
    """
    This class can be used to collect data from an API that includes the total number of results or pages in its
    response, and receives pagination parameters like ``page`` or ``limit`` and ``offset``. To create a spider that
    inherits from ``IndexSpider``:

    #. Set class attributes. Either:

        #. Set ``total_pages_pointer`` to the JSON Pointer for the total number of pages in the first response. The
           spider then yields a request for each page, incrementing a ``page`` query string parameter in each request.
        #. Set ``count_pointer`` to the JSON pointer for the total number of results, and set ``limit`` to the number
           of results to return per page, or to the JSON pointer for it. Optionally, set ``use_page`` to ``True`` to
           configure the spider to send a ``page`` query string parameter instead of a pair of ``limit`` and ``offset``
           query string parameters. The spider then yields a request for each offset/page.

    #. Write a ``start_requests`` method to yield the initial URL. The request's ``callback`` parameter should be set
       to ``self.parse_list``.

    If neither ``total_pages_pointer`` nor ``count_pointer`` can be used to create the URLs (e.g. if you need to query
    a separate URL that does not return JSON), you need to define ``range_generator`` and ``url_builder`` methods.
    ``range_generator`` should return page numbers or offset numbers. ``url_builder`` receives a page or offset from
    ``range_generator``, and returns a URL to request. See the ``kenya_makueni`` spider for an example.

    The names of the query string parameters 'page', 'limit' and 'offset' are customizable. Define the ``param_page``,
    ``param_limit`` and ``param_offset`` class attributes to set the custom names. Additional query string parameters
    can be added by defining ``additional_params``, which should be a dict.

    Th base URL is calculated from the initial URL yielded by ``start_requests``. If you need a different base URL for
    subsequent requests, define the ``base_url`` class attribute.

    By default, responses passed to ``parse_list`` are passed to the ``parse`` method from which items are yielded. If
    the responses passed to ``parse_list`` contain no OCDS data, set ``yield_list_results`` to ``False``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.param_page = getattr(self, 'param_page', 'page')
        self.param_limit = getattr(self, 'param_limit', 'limit')
        self.param_offset = getattr(self, 'param_offset', 'offset')
        self.additional_params = getattr(self, 'additional_params', {})
        self.base_url = getattr(self, 'base_url', '')
        self.yield_list_results = getattr(self, 'yield_list_results', True)

        if hasattr(self, 'total_pages_pointer') and self.total_pages_pointer:
            self.range_generator = self.pages_from_total_range_generator
            if not hasattr(self, 'url_builder'):
                self.url_builder = self.pages_url_builder
        elif hasattr(self, 'count_pointer') and self.count_pointer:
            if hasattr(self, 'use_page') and self.use_page:
                self.range_generator = self.page_size_range_generator
                if not hasattr(self, 'url_builder'):
                    self.url_builder = self.pages_url_builder
            else:
                self.range_generator = self.limit_offset_range_generator
                if not hasattr(self, 'url_builder'):
                    self.url_builder = self.limit_offset_url_builder

    @handle_http_error
    def parse_list(self, response, **kwargs):
        if self.yield_list_results:
            yield from self.parse(response)
        if not self.base_url:
            self._set_base_url(response.request.url)
        try:
            data = response.json()
        except ValueError:
            data = None
        for value in self.range_generator(data, response):
            yield self.build_request(self.url_builder(value, data, response), formatter=self.formatter, **kwargs)

    def pages_from_total_range_generator(self, data, response):
        pages = resolve_pointer(data, self.total_pages_pointer)
        return range(2, pages + 1)

    def pages_url_builder(self, value, data, response):
        return self._build_url({
            self.param_page: value,
        })

    def limit_offset_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.count_pointer)
        return range(self.limit, count, limit)

    def limit_offset_url_builder(self, value, data, response):
        return self._build_url({
            self.param_limit: self.limit,
            self.param_offset: value,
        })

    def page_size_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.count_pointer)
        # Assumes the first page is page 1, not page 0.
        return range(2, ceil(count / limit) + 1)

    def _resolve_limit(self, data):
        if isinstance(self.limit, str) and self.limit.startswith('/'):
            return resolve_pointer(data, self.limit)
        return int(self.limit)

    def _set_base_url(self, url):
        self.base_url = util.replace_parameters(url, page=None, limit=None, offset=None)

    def _build_url(self, params):
        url_params = params.copy()
        url_params.update(self.additional_params)
        return util.replace_parameters(self.base_url, **url_params)
