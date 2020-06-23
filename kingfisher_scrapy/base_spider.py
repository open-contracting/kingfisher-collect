import json
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import ijson
import scrapy
from jsonpointer import resolve_pointer

from kingfisher_scrapy import util
from kingfisher_scrapy.exceptions import KingfisherScrapyError, SpiderArgumentError
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.util import handle_http_error


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
    """

    MAX_SAMPLE = 10
    MAX_RELEASES_PER_PACKAGE = 100
    VALID_DATE_FORMATS = {'date': '%Y-%m-%d', 'datetime': '%Y-%m-%dT%H:%M:%S'}

    def __init__(self, sample=None, note=None, from_date=None, until_date=None,
                 date_format='date', *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://docs.scrapy.org/en/latest/topics/spiders.html#spider-arguments
        self.sample = sample == 'true'
        self.note = note
        self.from_date = from_date
        self.until_date = until_date
        self.date_format = self.VALID_DATE_FORMATS[date_format]

        spider_arguments = {
            'sample': sample,
            'note': note,
            'from_date': from_date,
            'until_date': until_date,
        }
        spider_arguments.update(kwargs)
        self.logger.info('Spider arguments: {!r}'.format(spider_arguments))

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        # Checks Spider date ranges arguments
        if spider.from_date or spider.until_date:
            if not spider.from_date:
                # Default to `default_from_date` class attribute.
                spider.from_date = spider.default_from_date
            if not spider.until_date:
                # Default to today.
                spider.until_date = datetime.now().strftime(spider.date_format)
            try:
                spider.from_date = datetime.strptime(spider.from_date, spider.date_format)
            except ValueError as e:
                raise SpiderArgumentError('spider argument from_date: invalid date value: {}'.format(e))
            try:
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
        return self.crawler.stats.get_value('start_time').strftime(format)

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
        if 'file_name' not in kwargs:
            kwargs['file_name'] = response.request.meta['file_name']
        if 'url' not in kwargs:
            kwargs['url'] = response.request.url
        if 'data' not in kwargs:
            kwargs['data'] = response.body
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


class ZipSpider(BaseSpider):
    """
    This class makes it easy to collect data from ZIP files. It assumes all files have the same data type.

    1. Inherit from ``ZipSpider``
    1. Set a ``data_type`` class attribute to the data type of the compressed files
    1. Optionally, set an ``encoding`` class attribute to the encoding of the compressed_files (default UTF-8)
    1. Optionally, set a ``zip_file_format`` class attribute to the format of the compressed files

       ``json_lines``
         Yields each line of the compressed files.
         The ZIP file is saved to disk.
       ``release_package``
         Re-packages the releases in the compressed files in groups of
         :const:`~kingfisher_scrapy.base_spider.BaseSpider.MAX_RELEASES_PER_PACKAGE`, and yields the packages.
         The ZIP file is saved to disk.
       ``None``
         Yields each compressed file.
         Each compressed file is saved to disk.

    1. Write a ``start_requests`` method to request the ZIP files

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spider import ZipSpider

        class MySpider(ZipSpider):
            name = 'my_spider'
            data_type = 'release_package'

            def start_requests(self):
                yield scrapy.Request('https://example.com/api/packages.zip', meta={'file_name': 'all.json'})
    """

    encoding = 'utf-8'
    zip_file_format = None

    @handle_http_error
    def parse(self, response):
        if self.zip_file_format:
            yield self.build_file_from_response(response, data_type='zip', post_to_api=False)

        zip_file = ZipFile(BytesIO(response.body))
        for finfo in zip_file.infolist():
            filename = finfo.filename
            if not filename.endswith('.json'):
                filename += '.json'

            data = zip_file.open(finfo.filename)

            kwargs = {
                'file_name': filename,
                'url': response.request.url,
                'data_type': self.data_type,
                'encoding': self.encoding,
            }

            if self.zip_file_format == 'json_lines':
                yield from self.parse_json_lines(data, **kwargs)
            elif self.zip_file_format == 'release_package':
                package = zip_file.open(finfo.filename)
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
    1. Optionally, set a ``next_pointer`` class attribute to the JSON Pointer for the next link (default "/links/next")
    1. Write a ``start_requests`` method to request the first page of API results

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

    def next_link(self, response):
        """
        If the JSON response has a ``links.next`` key, returns a ``scrapy.Request`` for the URL.
        """
        data = json.loads(response.text)
        url = resolve_pointer(data, self.next_pointer, None)
        if url:
            return self.build_request(url, formatter=self.next_page_formatter)

        if response.meta['depth'] == 0:
            raise KingfisherScrapyError('next link not found on the first page: {}'.format(response.url))
