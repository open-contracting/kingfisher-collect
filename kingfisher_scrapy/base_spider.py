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
from kingfisher_scrapy.util import handle_http_error, request_add_qs


class BaseSpider(scrapy.Spider):
    """
    Download a sample:

    .. code:: bash

        scrapy crawl spider_name -a sample=true

    Set the start date for range to download:

    .. code:: bash

        scrapy crawl spider_name -a from_date=2010-01-01

    Set the end date for range to download:

    .. code:: bash

        scrapy crawl spider_name -a until_date=2020-01-01

    Add a note to the collection:

    .. code:: bash

        scrapy crawl spider_name -a note='Started by NAME.'

    Each crawl writes data to its own directory. By default, this directory is named according to the time the crawl
    started. To override the time (for example, to force a new crawl to write to the same directory as an earlier
    crawl), you can set the crawl_time spider argument:

     .. code:: bash

        scrapy crawl spider_name -a crawl_time=2020-01-01T10:00:00

    Don't close the Kingfisher Process collection when the crawl finishes:

     .. code:: bash

        scrapy crawl spider_name -a keep_collection_open=true

    Add a GET parameter to the start URLs (returned by `start_requests`):

    .. code:: bash

        scrapy crawl spider_name -a qs=param1:value,param2:value2

    If the parameter value contains a comma, use a backslash to escape it:

    .. code:: bash

        scrapy crawl spider_name -a qs=param:value\\,value2
    """

    MAX_SAMPLE = 10
    MAX_RELEASES_PER_PACKAGE = 100
    VALID_DATE_FORMATS = {'date': '%Y-%m-%d', 'datetime': '%Y-%m-%dT%H:%M:%S'}

    ocds_version = '1.1'
    date_format = 'date'
    date_required = None

    def __init__(self, sample=None, note=None, from_date=None, until_date=None, crawl_time=None,
                 keep_collection_open=None, package_pointer=None, release_pointer=None, truncate=None, qs=None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        # https://docs.scrapy.org/en/latest/topics/spiders.html#spider-arguments
        self.sample = sample == 'true'
        self.note = note
        self.from_date = from_date
        self.until_date = until_date
        self.crawl_time = crawl_time
        self.keep_collection_open = keep_collection_open == 'true'
        # Pluck-related arguments.
        self.package_pointer = package_pointer
        self.release_pointer = release_pointer
        self.truncate = int(truncate) if truncate else None
        self.qs = qs

        self.date_format = self.VALID_DATE_FORMATS[self.date_format]
        self.date_required = self.date_required
        self.pluck = bool(package_pointer or release_pointer)

        if self.qs and hasattr(self, 'start_requests'):
            self.start_requests = request_add_qs(self.start_requests, qs)

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
            'qs': qs
        }
        spider_arguments.update(kwargs)
        self.logger.info('Spider arguments: {!r}'.format(spider_arguments))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        if spider.package_pointer and spider.release_pointer:
            raise SpiderArgumentError('You cannot specify both package_pointer and release_pointer spider arguments.')

        if spider.crawl_time:
            try:
                spider.crawl_time = datetime.strptime(spider.crawl_time, '%Y-%m-%dT%H:%M:%S')
            except ValueError as e:
                raise SpiderArgumentError('spider argument crawl_time: invalid date value: {}'.format(e))

        # Checks Spider date ranges arguments
        if spider.from_date or spider.until_date or spider.date_required:
            if not spider.from_date:
                # Default to `default_from_date` class attribute.
                spider.from_date = spider.default_from_date
            try:
                if isinstance(spider.from_date, str):
                    # convert to date format, if needed
                    spider.from_date = datetime.strptime(spider.from_date, spider.date_format)
            except ValueError as e:
                raise SpiderArgumentError('spider argument from_date: invalid date value: {}'.format(e))

            if not spider.until_date:
                spider.until_date = cls.get_default_until_date(spider)
            try:
                if isinstance(spider.until_date, str):
                    spider.until_date = datetime.strptime(spider.until_date, spider.date_format)
            except ValueError as e:
                raise SpiderArgumentError('spider argument until_date: invalid date value: {}'.format(e))

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

        To add a query string parameter to the file name:

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
        if not file_name.endswith(('.json', '.zip')):
            file_name += '.json'
        meta = {'file_name': file_name}
        if 'meta' in kwargs:
            meta.update(kwargs.pop('meta'))
        return scrapy.Request(url, meta=meta, **kwargs)

    def build_file_from_response(self, response, **kwargs):
        """
        Returns an item to yield, based on the response to a request.
        """
        kwargs.setdefault('file_name', response.request.meta['file_name'])
        kwargs.setdefault('url', response.request.url)
        kwargs.setdefault('data', response.body)
        return self.build_file(**kwargs)

    def build_file(self, *, file_name=None, url=None, data=None, data_type=None, encoding='utf-8', post_to_api=True):
        """
        Returns an item to yield.
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
        return FileItem({
            'number': number,
            'file_name': file_name,
            'data': data,
            'data_type': data_type,
            'url': url,
            'encoding': encoding,
        })

    def build_file_error_from_response(self, response, **kwargs):
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
            if self.sample and number > self.MAX_SAMPLE:
                break
            if isinstance(line, bytes):
                line = line.decode(encoding=encoding)
            yield self.build_file_item(number=number, file_name=file_name, url=url, data=line, data_type=data_type,
                                       encoding=encoding)

    def parse_json_array(self, f_package, f_list, *, file_name='data.json', url=None, data_type=None, encoding='utf-8',
                         array_field_name='releases'):
        if self.sample:
            size = self.MAX_SAMPLE
        else:
            size = self.MAX_RELEASES_PER_PACKAGE

        package = self._get_package_metadata(f_package, array_field_name)

        for number, items in enumerate(util.grouper(ijson.items(f_list, '{}.item'.format(array_field_name)), size), 1):
            package[array_field_name] = filter(None, items)
            data = json.dumps(package, default=util.default)
            yield self.build_file_item(number=number, file_name=file_name, url=url, data=data, data_type=data_type,
                                       encoding=encoding)
            if self.sample:
                break

    @classmethod
    def get_default_until_date(cls, spider):
        return datetime.now()


class SimpleSpider(BaseSpider):
    """
    Most spiders can inherit from this class. It assumes all responses have the same data type.

    1. Inherit from ``SimpleSpider``
    1. Set a ``data_type`` class attribute to the data type of the responses
    1. Optionally, set an ``encoding`` class attribute to the encoding of the responses (default UTF-8)
    1. Optionally, set a ``data_pointer`` class attribute to the JSON Pointer for OCDS data (default "")
    1. Write a ``start_requests`` method (and any intermediate callbacks) to send requests

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
            kwargs['data'] = json.dumps(resolve_pointer(json.loads(response.text), self.data_pointer)).encode()

        yield self.build_file_from_response(response, data_type=self.data_type, encoding=self.encoding, **kwargs)


class CompressedFileSpider(BaseSpider):
    """
    This class makes it easy to collect data from ZIP or RAR files. It assumes all files have the same data type.

    1. Inherit from ``CompressedFileSpider``
    1. Set a ``data_type`` class attribute to the data type of the compressed files
    1. Optionally, set an ``encoding`` class attribute to the encoding of the compressed files (default UTF-8)
    1. Optionally, set a ``archive_format`` class attribute to the archive file format ("zip" or "rar").
    1. Optionally, set a ``compressed_file_format`` class attribute to the format of the compressed files

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

    1. Write a ``start_requests`` method to request the archive files

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
    archive_format = 'zip'
    file_name_must_contain = ''

    @handle_http_error
    def parse(self, response):
        if self.compressed_file_format:
            yield self.build_file_from_response(response, data_type=self.archive_format, post_to_api=False)
        if self.archive_format == 'zip':
            cls = ZipFile
        else:
            cls = RarFile
        archive_file = cls(BytesIO(response.body))
        for file_info in archive_file.infolist():
            filename = file_info.filename
            basename = os.path.basename(filename)
            if self.file_name_must_contain not in basename:
                continue
            if self.archive_format == 'rar' and file_info.isdir():
                continue
            if self.archive_format == 'zip' and file_info.is_dir():
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

    1. Inherit from ``LinksSpider``
    1. Set a ``data_type`` class attribute to the data type of the API responses
    1. Set a ``next_page_formatter`` class attribute to set the file name as in
       :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_request`
    1. Write a ``start_requests`` method to request the first page of API results
    1. Optionally, set a ``next_pointer`` class attribute to the JSON Pointer for the next link (default "/links/next")

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

        if not self.sample:
            yield self.next_link(response)

    def next_link(self, response, **kwargs):
        """
        If the JSON response has a ``links.next`` key, returns a ``scrapy.Request`` for the URL.
        """
        data = json.loads(response.text)
        url = resolve_pointer(data, self.next_pointer, None)
        if url:
            return self.build_request(url, formatter=self.next_page_formatter, **kwargs)

        if response.meta['depth'] == 0:
            raise MissingNextLinkError('next link not found on the first page: {}'.format(response.url))


class PeriodicalSpider(SimpleSpider):
    """
    This class helps to crawl urls that receive a year (YYYY) or a month and year (YYYY-mm) as parameters. To use it:

    1. Extend from ``PeriodicalSpider``.
    1. Set the ``date_format`` attribute if it's not defined already. Valid values are 'year' and 'year-month'.
    1. Set a ``default_from_date`` year or month-year.
    1. Optionally, set a ``default_until_date`` year or month-year. If absent, ``default_until_date`` defaults to the
    current year or month-year.
    1. Set the ``pattern`` parameter with the url to retrieve.
    1. Implement the `get_formatter` method.

    The ``pattern`` should include a placeholder for a year or month-year parameter. With the year parameter, an int is
    passed. If the year-month parameter is used, a ``Date`` instance is passed. Example:

    .. code-block: python

        url = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'

    When the ``sample`` option is used, the latest year or month of data is retrieved.
    """
    VALID_DATE_FORMATS = {'year': '%Y', 'year-month': '%Y-%m'}

    def __init__(self, *args, **kwargs):
        self.date_format_key = self.date_format
        super().__init__(*args, **kwargs)

        if hasattr(self, 'start_requests_callback'):
            self.start_requests_callback = getattr(self, self.start_requests_callback)
        else:
            self.start_requests_callback = self.parse

    @classmethod
    def from_crawler(cls, crawler, from_date=None, *args, **kwargs):
        if not from_date:
            from_date = cls.default_from_date

        spider = super(SimpleSpider, cls).from_crawler(crawler, from_date=from_date, *args, **kwargs)

        return spider

    @classmethod
    def get_default_until_date(cls, spider):
        if hasattr(spider, 'default_until_date') and spider.default_until_date:
            return spider.default_until_date
        else:
            return datetime.today()

    def start_requests(self):

        start = self.from_date

        stop = self.until_date

        if self.sample:
            start = stop

        if self.date_format_key == 'year':
            date_range = util.date_range_by_year(start.year, stop.year)
        else:
            date_range = util.date_range_by_month(start, stop)

        for date in date_range:
            for url in self.build_urls(self.pattern, date):
                yield self.build_request(url, self.get_formatter(), callback=self.start_requests_callback)

    @abstractmethod
    def get_formatter(self):
        pass

    def build_urls(self, pattern, date):
        yield pattern.format(date)


class IndexSpider(SimpleSpider):
    """
    This class can be used to collect data from an API which includes the total number of results or pages in their
    response data, and receives pagination parameters like ``page``, ``limit`` and ``offset``. The values for the
    parameters are calculated and the requests are sent to the Scrapy's pipeline at the same time. To create a spider
    that inherits from ``IndexSpider``:

    1. Set a pointer to the attribute that contains the total number of pages or elements in the response data for the
    first request to the API:
        1. Set ``total_pages_pointer`` to point to the JSON element that contains the total number of pages in the
        response data. The API will add the 'page' GET parameter to the URL in the subsequent requests.
        1. Set ``count_pointer`` to point to the JSON element with the total number of results. If you use
        ``count_pointer``, you must set ``limit`` to indicate the number of results to return for each page. The
        ``limit`` attribute can either a number or a JSON pointer. Optionally, set ``use_page`` to ``True``
        to calculate a 'page' parameter instead of the 'limit' and 'offset'.
    1. Write a ``start_request`` method with a request to the initial URL. The request's callback should be set to
    ``self.parse_list``.

    If neither ``total_pages_counter`` nor ``count_pointer`` can be used to create the URLs (e.g. if you need to query
    a separate URL that does not return JSON), you can provide a custom range of parameters defining the
    ``range_generator`` method. This method should return page or offset numbers. You also need to define a
    ``build_url`` method, that receives the pages/offset generated by ``range_generator``. See the ``kenya_makueni``
    spider for an example.

    The names of the GET parameters 'page', 'limit' and 'offset' to include in the URLS are customizable. Define the
    ``param_page``, ``param_limit`` and ``param_offset`` class members to set the custom names. Any additional GET
    parameters can be added by defining ``additional_params``, which should be a dictionary.

    Th base URL is taken from the first URL yielded by ``start_requests``. If you need a different URL for the pages,
    define the ``base_url`` class member.

    By default the content received in ``parse_list`` is yielded. If you want to avoid this, set ``yield_list_results``
    to ``False``.

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
            data = json.loads(response.text)
        except json.JSONDecodeError:
            data = None
        if self.sample:
            return
        for generated_params in self.range_generator(data, response):
            yield self.build_request(self.url_builder(generated_params, data, response), formatter=self.formatter,
                                     **kwargs)

    def pages_from_total_range_generator(self, data, response):
        pages = resolve_pointer(data, self.total_pages_pointer)
        return range(2, pages + 1)

    def pages_url_builder(self, params, data, response):
        return self._build_url({
            self.param_page: params
        })

    def limit_offset_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.count_pointer)
        return range(self.limit, count, limit)

    def limit_offset_url_builder(self, params, data, response):
        return self._build_url({
            self.param_limit: self.limit,
            self.param_offset: params
        })

    def page_size_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.count_pointer)
        return range(2, (ceil(count/limit))+1)

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
