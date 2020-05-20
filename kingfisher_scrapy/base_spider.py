import hashlib
import json
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import ijson
import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.exceptions import SpiderArgumentError


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
        self.from_date = from_date
        self.until_date = until_date
        self.note = note
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
                # 'from_date' defaults to 'default_from_date' spider class attribute
                spider.from_date = spider.default_from_date
            if not spider.until_date:
                # 'until_date' defaults to today
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

    def save_response_to_disk(self, response, filename, data_type=None, encoding='utf-8', post_to_api=True):
        """
        Returns an item to yield, based on the response to a request.
        """
        return self.save_data_to_disk(response.body, filename, response.request.url, data_type, encoding,
                                      post_to_api)

    def save_data_to_disk(self, data, filename, url=None, data_type=None, encoding='utf-8', post_to_api=True):
        """
        Returns an item to yield
        """
        return {
            'data': data,
            'file_name': filename,
            'url': url,
            'data_type': data_type,
            'encoding': encoding,
            'success': True,
            'post_to_api': post_to_api,
        }

    def get_start_time(self, format):
        """
        Returns the formatted start time of the crawl.
        """
        return self.crawler.stats.get_value('start_time').strftime(format)

    def _build_file_item(self, number, line, data_type, url, encoding, file_name):
        return {
            'success': True,
            'number': number,
            'file_name': file_name,
            'data': line,
            'data_type': data_type,
            'url': url,
            'encoding': encoding,
            'post_to_api': True
        }

    def parse_json_lines(self, f, data_type, url, encoding='utf-8', file_name='data.json'):
        for number, line in enumerate(f, 1):
            if self.sample and number > self.MAX_SAMPLE:
                break
            if isinstance(line, bytes):
                line = line.decode(encoding=encoding)
            yield self._build_file_item(number, line, data_type, url, encoding, file_name)

    def get_package(self, f, array_name):
        """
        Returns the package data from a array_name_package object
        """
        package = {}
        for item in util.items(ijson.parse(f), '', array_name=array_name):
            package.update(item)
        return package

    def parse_json_array(self, f_package, f_list, data_type, url, encoding='utf-8',
                         array_field_name='releases', file_name='data.json'):
        if self.sample:
            size = self.MAX_SAMPLE
        else:
            size = self.MAX_RELEASES_PER_PACKAGE

        package = self.get_package(f_package, array_field_name)

        for number, items in enumerate(util.grouper(ijson.items(f_list, '{}.item'.format(array_field_name)), size), 1):
            package[array_field_name] = filter(None, items)
            yield self._build_file_item(number, json.dumps(package, default=util.default), data_type, url, encoding,
                                        file_name)
            if self.sample:
                break


class ZipSpider(BaseSpider):
    def parse_zipfile(self, response, data_type, file_format=None, encoding='utf-8'):
        """
        Handling response with JSON data in ZIP files

        :param str file_format: The zipped file's format. If this is set to "json_lines", then each line of the zipped
            file will be yielded separately. If this is set to "release_package", then the releases will be re-packaged
            in groups of :const:`~kingfisher_scrapy.base_spider.BaseSpider.MAX_RELEASES_PER_PACKAGE` and yielded. In
            both cases, only the zipped file will be saved to disk. If this is not set, the file will be yielded and
            saved to disk.
        :param response response: the response that contains the zip file.
        :param str data_type: the zipped files data_type
        :param str encoding: the zipped files encoding. Default to utf-8
        """
        if response.status == 200:
            if file_format:
                self.save_response_to_disk(response, '{}.zip'.format(hashlib.md5(response.url.encode('utf-8'))
                                                                     .hexdigest()),
                                           post_to_api=False)
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
                    yield self.save_data_to_disk(data.read(), filename, data_type=data_type, url=response.request.url,
                                                 encoding=encoding)
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }


class LinksSpider(BaseSpider):
    @staticmethod
    def next_link(response):
        """
        Handling API response with a links field

        Access to ``links/next`` for the new url, and returns a Request
        """
        json_data = json.loads(response.text)
        if 'links' in json_data and 'next' in json_data['links']:
            url = json_data['links']['next']
            return scrapy.Request(
                url=url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )

    def parse_next_link(self, response, data_type):
        if response.status == 200:

            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type=data_type)

            if not self.sample:
                yield self.next_link(response)
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
