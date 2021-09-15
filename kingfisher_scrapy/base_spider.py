import codecs
import os
from abc import abstractmethod
from datetime import datetime
from io import BytesIO
from math import ceil
from zipfile import ZipFile

import scrapy
from jsonpointer import resolve_pointer
from rarfile import RarFile

from kingfisher_scrapy import util
from kingfisher_scrapy.exceptions import (IncoherentConfigurationError, MissingNextLinkError, SpiderArgumentError,
                                          UnknownArchiveFormatError)
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.util import (add_path_components, add_query_string, get_file_name_and_extension,
                                    handle_http_error, parameters)

browser_user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'  # noqa: E501


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
    -  If the JSON file is concatenated JSON or line-delimited JSON and the root path is to a JSON array, set a
       ``root_path_max_length`` class attribute to the maximum length of the JSON array at the root path.
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

    # Not to be overridden by sub-classes.
    available_steps = {'compile', 'check'}

    def __init__(self, sample=None, path=None, from_date=None, until_date=None, crawl_time=None, note=None,
                 keep_collection_open=None, steps=None, compile_releases=None, package_pointer=None,
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

        # Related to incremental crawls.
        self.crawl_time = crawl_time

        # Related to Kingfisher Process.
        self.note = note
        self.keep_collection_open = keep_collection_open == 'true'
        if steps is None:
            self.steps = self.available_steps
        else:
            self.steps = set(steps.split(',')) & self.available_steps

        # Related to the DatabaseStore extension.
        self.compile_releases = compile_releases == 'true'

        # Related to the pluck command.
        self.package_pointer = package_pointer
        self.release_pointer = release_pointer
        self.truncate = int(truncate) if truncate else None

        self.query_string_parameters = {}
        for key, value in kwargs.items():
            if key.startswith('qs:'):
                self.query_string_parameters[key[3:]] = value

        self.date_format = self.VALID_DATE_FORMATS[self.date_format]
        self.pluck = bool(package_pointer or release_pointer)

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

        # DatabaseStore-related logic.
        if crawler.settings['DATABASE_URL']:
            if not spider.crawl_time:
                raise SpiderArgumentError("spider argument `crawl_time`: can't be blank if `DATABASE_URL` is set")
            if spider.compile_releases and 'record' in getattr(spider, 'data_type', ''):
                raise SpiderArgumentError("spider argument `compile_releases`: can't be set if spider returns records")

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
        have a ``.json``, ``.csv``, ``.xlsx``, ``.rar`` or ``.zip`` extension, it adds a ``.json`` extension.

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


class SimpleSpider(BaseSpider):
    """
    Most spiders can inherit from this class. It assumes all responses have the same data type.

    #. Inherit from ``SimpleSpider``
    #. Set a ``data_type`` class attribute to the data type of the responses
    #. Write a ``start_requests`` method (and any intermediate callbacks) to send requests

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spider import SimpleSpider

        class MySpider(SimpleSpider):
            name = 'my_spider'

            # SimpleSpider
            data_type = 'release_package'

            def start_requests(self):
                yield scrapy.Request('https://example.com/api/package.json', meta={'file_name': 'all.json'})
    """

    @handle_http_error
    def parse(self, response):
        yield self.build_file_from_response(response, data_type=self.data_type)


class CompressedFileSpider(BaseSpider):
    """
    This class makes it easy to collect data from ZIP or RAR files. It assumes all files have the same data type.
    Each compressed file is saved to disk. The archive file is *not* saved to disk.

    #. Inherit from ``CompressedFileSpider``
    #. Set a ``data_type`` class attribute to the data type of the compressed files
    #. Optionally, add a ``resize_package = True`` class attribute to split large packages (e.g. greater than 100MB)
    #. Write a ``start_requests`` method to request the archive files

    .. code-block:: python

        from kingfisher_scrapy.base_spider import CompressedFileSpider
        from kingfisher_scrapy.util import components

        class MySpider(CompressedFileSpider):
            name = 'my_spider'

            # CompressedFileSpider
            data_type = 'release_package'

            def start_requests(self):
                yield self.build_request('https://example.com/api/packages.zip', formatter=components(-1))

    .. note::

       ``concatenated_json = True``, ``line_delimited = True``, ``root_path``, ``data_type = 'release'`` and
       ``data_type = 'record'`` are not supported if ``resize_package = True``.
    """

    # BaseSpider
    dont_truncate = True

    resize_package = False
    file_name_must_contain = ''

    @handle_http_error
    def parse(self, response):
        archive_name, archive_format = get_file_name_and_extension(response.request.meta['file_name'])

        if archive_format == 'zip':
            cls = ZipFile
        elif archive_format == 'rar':
            cls = RarFile
        else:
            raise UnknownArchiveFormatError(response.request.meta['file_name'])

        # If we use a context manager here, the archive file might close before the item pipeline reads from the file
        # handlers of the compressed files.
        archive_file = cls(BytesIO(response.body))

        number = 1
        for file_info in archive_file.infolist():
            # Avoid reading the rest of a large file, since the rest of the items will be dropped.
            if self.sample and number > self.sample:
                break

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

            compressed_file = archive_file.open(filename)

            # If `resize_package = True`, then we need to open the file twice: once to extract the package metadata and
            # then to extract the releases themselves.
            if self.resize_package:
                data = {'data': compressed_file, 'package': archive_file.open(filename)}
            else:
                data = compressed_file

            yield File({
                'file_name': f'{archive_name}-{basename}',
                'data': data,
                'data_type': self.data_type,
                'url': response.request.url,
            })

            number += 1


class LinksSpider(SimpleSpider):
    """
    This class makes it easy to collect data from an API that implements the `pagination
    <https://github.com/open-contracting-extensions/ocds_pagination_extension>`__ pattern:

    #. Inherit from ``LinksSpider``
    #. Set a ``data_type`` class attribute to the data type of the API responses
    #. Set a ``next_page_formatter`` class attribute to set the file name like in
       :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_request`
    #. Write a ``start_requests`` method to request the first page of API results
    #. Optionally, set a ``next_pointer`` class attribute to the JSON Pointer for the next link (default "/links/next")

    If the API returns the number of total pages or results in the response, consider using ``IndexSpider`` instead.

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spider import LinksSpider

        class MySpider(LinksSpider):
            name = 'my_spider'

            # SimpleSpider
            data_type = 'release_package'

            # LinksSpider
            next_page_formatter = staticmethod(parameters('page'))

            def start_requests(self):
                yield scrapy.Request('https://example.com/api/packages.json', meta={'file_name': 'page-1.json'})

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
        # If the sample size is 1, we don't want to parse the response, especially if --max-bytes is used.
        if self.sample and self.sample == 1:
            return

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

    #. Set a ``formatter`` class attribute to set the file name like in
       :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_request`
    #. Set a ``default_from_date`` class attribute to a year ("YYYY") or year-month ("YYYY-MM")
    #. If the source stopped publishing, set a ``default_until_date`` class attribute to a year or year-month
    #. Optionally, set a ``start_requests_callback`` class attribute to a method's name as a string - otherwise, it
       defaults to :meth:`~kingfisher_scrapy.base_spider.SimpleSpider.parse`

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

    #. If the ``page`` query string parameter is zero-indexed, set ``start_page = 0``.
    #. Set ``formatter`` to set the file name like in :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_request`.
       If ``total_pages_pointer`` or ``use_page = True``, it defaults to ``parameters(<param_page>)``. Otherwise, if
       ``count_pointer`` is set and ``use_page = False``, it defaults to ``parameters(<param_offset>)``.
    #. Write a ``start_requests`` method to yield the initial URL. The request's ``callback`` parameter should be set
       to ``self.parse_list``.

    If neither ``total_pages_pointer`` nor ``count_pointer`` can be used to create the URLs (e.g. if you need to query
    a separate URL that does not return JSON), you need to define ``range_generator`` and ``url_builder`` methods.
    ``range_generator`` should return page numbers or offset numbers. ``url_builder`` receives a page or offset from
    ``range_generator``, and returns a URL to request. See the ``kenya_makueni`` spider for an example.

    If the results are in ascending chronological order, set ``chronological_order = 'asc'``.

    The ``parse_list`` method parses responses as JSON data. To change the parser of these responses - for example,
    to check for an error response, or to extract the page count from an HTML page - override the ``parse_list_loader``
    method. If this method returns a ``FileError``, then ``parse_list`` yields it and returns.

    Otherwise, results are yielded from all responses by :meth:`~kingfisher_scrapy.base_spider.SimpleSpider.parse`. To
    change this method, set a ``parse_list_callback`` class attribute to a method's name as a string.

    The names of the query string parameters 'page', 'limit' and 'offset' are customizable. Define the ``param_page``,
    ``param_limit`` and ``param_offset`` class attributes to set the custom names.

    If a different URL is used for the initial request than for later requests, set the ``base_url`` class attribute
    to the base URL of later requests. In this case, results aren't yielded from the response passed to ``parse_list``.
    """

    use_page = False
    start_page = 1
    chronological_order = 'desc'
    parse_list_callback = 'parse'
    param_page = 'page'
    param_limit = 'limit'
    param_offset = 'offset'
    base_url = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parse_list_callback = getattr(self, self.parse_list_callback)

        has_total_pages_pointer = hasattr(self, 'total_pages_pointer')
        has_count_pointer = hasattr(self, 'count_pointer')
        has_range_generator = hasattr(self, 'range_generator')

        if not (has_total_pages_pointer ^ has_count_pointer ^ has_range_generator):
            raise IncoherentConfigurationError(
                'Exactly one of total_pages_pointer, count_pointer or range_generator must be set.')
        if self.use_page and not has_count_pointer:
            raise IncoherentConfigurationError(
                'use_page = True has no effect unless count_pointer is set.')

        if has_total_pages_pointer:
            self.range_generator = self.pages_from_total_range_generator
            if not hasattr(self, 'url_builder'):
                self.url_builder = self.pages_url_builder
            if not hasattr(self, 'formatter'):
                self.formatter = parameters(self.param_page)
        elif has_count_pointer:
            if self.use_page:
                self.range_generator = self.page_size_range_generator
                if not hasattr(self, 'url_builder'):
                    self.url_builder = self.pages_url_builder
                if not hasattr(self, 'formatter'):
                    self.formatter = parameters(self.param_page)
            else:
                self.range_generator = self.limit_offset_range_generator
                if not hasattr(self, 'url_builder'):
                    self.url_builder = self.limit_offset_url_builder
                if not hasattr(self, 'formatter'):
                    self.formatter = parameters(self.param_offset)

    @handle_http_error
    def parse_list(self, response):
        data = self.parse_list_loader(response)
        if isinstance(data, FileError):
            yield data
            return

        if not self.base_url:
            yield from self.parse_list_callback(response)

        for priority, value in enumerate(self.range_generator(data, response)):
            # Requests with a higher priority value will execute earlier and we want the newest pages first.
            # https://doc.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Request
            if self.chronological_order == 'desc':
                priority *= -1
            yield self.build_request(self.url_builder(value, data, response), formatter=self.formatter,
                                     priority=priority, callback=self.parse_list_callback)

    def parse_list_loader(self, response):
        return response.json()

    def pages_from_total_range_generator(self, data, response):
        pages = resolve_pointer(data, self.total_pages_pointer)
        if self.base_url:
            start = 0
        else:
            start = 1
        return range(self.start_page + start, self.start_page + pages)

    def pages_url_builder(self, value, data, response):
        return self._build_url(response, {
            self.param_page: value,
        })

    def limit_offset_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.count_pointer)
        if self.base_url:
            start = 0
        else:
            start = limit
        return range(start, count, limit)

    def limit_offset_url_builder(self, value, data, response):
        limit = self._resolve_limit(data)
        return self._build_url(response, {
            self.param_limit: limit,
            self.param_offset: value,
        })

    def page_size_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.count_pointer)
        if self.base_url:
            start = 0
        else:
            start = 1
        return range(self.start_page + start, self.start_page + ceil(count / limit))

    def _resolve_limit(self, data):
        if isinstance(self.limit, str) and self.limit.startswith('/'):
            return resolve_pointer(data, self.limit)
        return int(self.limit)

    def _build_url(self, response, params):
        return util.replace_parameters(self.base_url or response.request.url, **params.copy())


class BigFileSpider(SimpleSpider):
    """
    This class makes it easy to collect data from sources that provide big JSON files as a release package.
    Each big file is resized to multiple small files that the current version of Kingfisher process is able to process.

    #. Inherit from ``BigFileSpider``
    #. Write a ``start_requests`` method to request the archive files

    .. code-block:: python

        from kingfisher_scrapy.base_spider import BigFileSpider
        from kingfisher_scrapy.util import components

        class MySpider(BigFileSpider):
            name = 'my_spider'

            def start_requests(self):
                yield self.build_request('https://example.com/api/package.json', formatter=components(-1)

    .. note::

       ``concatenated_json = True``, ``line_delimited = True`` and ``root_path`` are not supported.
    """

    resize_package = True

    @handle_http_error
    def parse(self, response):
        data = {'data': response.body,
                'package': response.body}
        yield self.build_file(file_name=response.request.meta['file_name'], url=response.request.url,
                              data_type='release_package', data=data)
