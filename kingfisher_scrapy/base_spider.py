import hashlib
import json
import os
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
    VALID_DATE_FORMATS = {'year_month_day': '%Y-%m-%d', 'year_month_day_time': '%Y-%m-%dT%H:%M:%S'}

    def __init__(self, sample=None, note=None, from_date=None, until_date=None,
                 date_format='year_month_day', *args, **kwargs):
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

    def get_local_file_path_including_filestore(self, filename):
        """
        Prepends Scrapy's storage directory and the crawl's relative directory to the filename.
        """
        return os.path.join(self.crawler.settings['FILES_STORE'], self._get_crawl_path(), filename)

    def get_local_file_path_excluding_filestore(self, filename):
        """
        Prepends the crawl's relative directory to the filename.
        """
        return os.path.join(self._get_crawl_path(), filename)

    def save_response_to_disk(self, response, filename, data_type=None, encoding='utf-8'):
        """
        Writes the response's body to the filename in the crawl's directory.

        Writes a ``<filename>.fileinfo`` metadata file in the crawl's directory, and returns a dict with the metadata.
        """
        return self._save_response_to_disk(response.body, filename, response.request.url, data_type, encoding)

    def save_data_to_disk(self, data, filename, url=None, data_type=None, encoding='utf-8'):
        """
        Writes the data to the filename in the crawl's directory.

        Writes a ``<filename>.fileinfo`` metadata file in the crawl's directory, and returns a dict with the metadata.
        """
        return self._save_response_to_disk(data, filename, url, data_type, encoding)

    def get_start_time(self, format):
        """
        Returns the formatted start time of the crawl.
        """
        return self.crawler.stats.get_value('start_time').strftime(format)

    def _save_response_to_disk(self, data, filename, url, data_type, encoding):
        self._write_file(filename, data)

        metadata = {
            'url': url,
            'data_type': data_type,
            'encoding': encoding,
        }

        self._write_file(filename + '.fileinfo', metadata)

        metadata['success'] = True
        metadata['file_name'] = filename

        return metadata

    def _write_file(self, filename, data):
        path = self.get_local_file_path_including_filestore(filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if isinstance(data, bytes):
            mode = 'wb'
        else:
            mode = 'w'

        with open(path, mode) as f:
            if isinstance(data, (bytes, str)):
                f.write(data)
            else:
                json.dump(data, f)

    def _get_crawl_path(self):
        name = self.name
        if self.sample:
            name += '_sample'
        return os.path.join(name, self.get_start_time('%Y%m%d_%H%M%S'))

    def _build_file_item(self, number, line, data_type, url, encoding):
        return {
            'success': True,
            'number': number,
            'file_name': 'data.json',
            'data': line,
            'data_type': data_type,
            'url': url,
            'encoding': encoding,
        }

    def parse_json_lines(self, f, data_type, url, encoding='utf-8'):
        for number, line in enumerate(f, 1):
            if self.sample and number > self.MAX_SAMPLE:
                break
            if isinstance(line, bytes):
                line = line.decode(encoding=encoding)
            yield self._build_file_item(number, line, data_type, url, encoding)

    def get_package(self, f, array_name):
        """
        Returns the package data from a array_name_package object
        """
        package = {}
        for item in util.items(ijson.parse(f), '', array_name=array_name):
            package.update(item)
        return package

    def parse_json_array(self, f_package, f_list, data_type, url, encoding='utf-8', array_field_name='releases'):
        if self.sample:
            size = self.MAX_SAMPLE
        else:
            size = self.MAX_RELEASES_PER_PACKAGE

        package = self.get_package(f_package, array_field_name)

        for number, items in enumerate(util.grouper(ijson.items(f_list, '{}.item'.format(array_field_name)), size), 1):
            package[array_field_name] = filter(None, items)
            yield self._build_file_item(number, json.dumps(package, default=util.default), data_type, url, encoding)
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
                                                                     .hexdigest()))
            zip_file = ZipFile(BytesIO(response.body))
            for finfo in zip_file.infolist():
                filename = finfo.filename
                if not filename.endswith('.json'):
                    filename += '.json'
                data = zip_file.open(finfo.filename)
                if file_format == 'json_lines':
                    yield from self.parse_json_lines(data, data_type, response.request.url, encoding=encoding)
                elif file_format == 'release_package':
                    package = zip_file.open(finfo.filename)
                    yield from self.parse_json_array(package, data, data_type, response.request.url,
                                                     encoding=encoding)
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
