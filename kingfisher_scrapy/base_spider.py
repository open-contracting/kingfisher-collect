import hashlib
import json
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import ijson
import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.util import handle_error


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
        return 200 <= response.status < 300

    def get_start_time(self, format):
        """
        Returns the formatted start time of the crawl.
        """
        return self.crawler.stats.get_value('start_time').strftime(format)

    def build_file_from_response(self, response, filename, data_type=None, encoding='utf-8', post_to_api=True):
        """
        Returns an item to yield, based on the response to a request.
        """
        return self.build_file(response.body, filename, response.request.url, data_type, encoding, post_to_api)

    def build_file(self, data, filename, url=None, data_type=None, encoding='utf-8', post_to_api=True):
        """
        Returns an item to yield.
        """
        return File({
            'file_name': filename,
            'data': data,
            'data_type': data_type,
            'url': url,
            'encoding': encoding,
            'post_to_api': post_to_api,
        })

    def build_file_item(self, number, data, data_type, url, encoding, file_name):
        return FileItem({
            'number': number,
            'file_name': file_name,
            'data': data,
            'data_type': data_type,
            'url': url,
            'encoding': encoding,
        })

    def build_file_error_from_response(self, response, **kwargs):
        file_error = {
            'url': response.request.url,
            'errors': {'http_code': response.status},
        }
        if 'kf_filename' in response.request.meta:
            file_error['file_name'] = response.request.meta['kf_filename']
        file_error.update(kwargs)
        return FileError(file_error)

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

    def parse_json_lines(self, f, data_type, url, encoding='utf-8', file_name='data.json'):
        for number, line in enumerate(f, 1):
            if self.sample and number > self.MAX_SAMPLE:
                break
            if isinstance(line, bytes):
                line = line.decode(encoding=encoding)
            yield self.build_file_item(number, line, data_type, url, encoding, file_name)

    def parse_json_array(self, f_package, f_list, data_type, url, encoding='utf-8', array_field_name='releases',
                         file_name='data.json'):
        if self.sample:
            size = self.MAX_SAMPLE
        else:
            size = self.MAX_RELEASES_PER_PACKAGE

        package = self._get_package_metadata(f_package, array_field_name)

        for number, items in enumerate(util.grouper(ijson.items(f_list, '{}.item'.format(array_field_name)), size), 1):
            package[array_field_name] = filter(None, items)
            data = json.dumps(package, default=util.default)
            yield self.build_file_item(number, data, data_type, url, encoding, file_name)
            if self.sample:
                break


class ZipSpider(BaseSpider):
    """
    This class makes it easy to collect data from ZIP files:

    -  Inherit from ``ZipSpider``
    -  Set a ``parse_zipfile_kwargs`` class attribute to the keyword arguments for the
       :meth:`kingfisher_scrapy.base_spider.ZipSpider.parse_zipfile` method
    -  Write a ``start_requests`` method to request the ZIP files

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spider import ZipSpider

        class MySpider(LinksSpider):
            name = 'my_spider'

            parse_zipfile_kwargs = {'data_type': 'release_package'}

            def start_requests(self):
                yield scrapy.Request(
                    url='https://example.com/api/packages.zip',
                    meta={'kf_filename': 'all.json'}
                )
    """
    @handle_error
    def parse(self, response):
        yield from self.parse_zipfile(response, **self.parse_zipfile_kwargs)

    def parse_zipfile(self, response, data_type, file_format=None, encoding='utf-8'):
        """
        Handles a response that is a ZIP file.

        :param response response: the response
        :param str data_type: the compressed files' ``data_type``
        :param str file_format: The compressed files' format

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
        :param str encoding: the compressed files' encoding
        """
        if file_format:
            filename = '{}.zip'.format(hashlib.md5(response.url.encode('utf-8')).hexdigest())
            self.build_file_from_response(response, filename, post_to_api=False)

        zip_file = ZipFile(BytesIO(response.body))
        for finfo in zip_file.infolist():
            filename = finfo.filename
            if not filename.endswith('.json'):
                filename += '.json'

            data = zip_file.open(finfo.filename)

            if file_format == 'json_lines':
                yield from self.parse_json_lines(data, data_type, response.request.url, encoding=encoding,
                                                 file_name=filename)
            elif file_format == 'release_package':
                package = zip_file.open(finfo.filename)
                yield from self.parse_json_array(package, data, data_type, response.request.url,
                                                 encoding=encoding, file_name=filename)
            else:
                yield self.build_file(data.read(), filename, data_type=data_type, url=response.request.url,
                                      encoding=encoding)


class LinksSpider(BaseSpider):
    """
    This class makes it easy to collect data from an API that implements the `pagination
    <https://github.com/open-contracting-extensions/ocds_pagination_extension>`__ pattern:

    -  Inherit from ``LinksSpider``
    -  Set a ``data_type`` class attribute to the data type of the API responses
    -  Write a ``start_requests`` method to request the first page

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spider import LinksSpider

        class MySpider(LinksSpider):
            name = 'my_spider'
            data_type = 'release_package'

            def start_requests(self):
                yield scrapy.Request(
                    url='https://example.com/api/packages.json',
                    meta={'kf_filename': 'page1.json'}
                )
    """

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, response.request.meta['kf_filename'], data_type=self.data_type)

        if not self.sample:
            yield self.next_link(response)

    @staticmethod
    def next_link(response):
        """
        If the JSON response has a ``links.next`` key, returns a ``scrapy.Request`` for the URL.
        """
        data = json.loads(response.text)
        if 'links' in data and 'next' in data['links']:
            url = data['links']['next']
            return scrapy.Request(url, meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'})
