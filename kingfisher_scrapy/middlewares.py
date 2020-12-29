# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
from datetime import datetime

import ijson
import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.items import File


class ParaguayAuthMiddleware:
    """
    Downloader middleware that manages API authentication for Paraguay scrapers.

    Both DNCP (procurement authority) and Hacienda (finance ministry) use an authentication protocol based on OAuth 2.

    This middleware helps us to manage the protocol, which consists on acquiring an access token every x minutes
    (usually 15) and sending the token on each request. The acquisition method of the token is delegated to the spider,
    since each publisher has their own credentials and requirements.

    Apparently, a Downloader Middleware is the best place to set HTTP Request Headers (see
    https://docs.scrapy.org/en/latest/topics/architecture.html), but it's not enough for this case :(.
    Tokens should be generated and assigned just before sending a request, but Scrapy does not provide any way to do
    this, which in turn means that sometimes we accidently send expired tokens. For now, the issue seems to be avoided
    by setting the number of concurrent requests to 1, at cost of download speed.
    """

    def __init__(self, spider):
        spider.logger.info('Initialized authentication middleware with spider: %s.', spider.name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        if 'auth' in request.meta and request.meta['auth'] is False:
            return
        if spider.auth_failed:
            spider.logger.error('Fatal: no authentication token, stopping now...')
            spider.crawler.stop()
            raise scrapy.exceptions.IgnoreRequest()
        request.headers['Authorization'] = spider.access_token
        if self._expires_soon(spider):
            # SAVE the last request to continue after getting the token
            spider.last_request = request
            # spider MUST implement the request_access_token method
            return spider.request_access_token()

    def process_response(self, request, response, spider):
        if response.status == 401 or response.status == 429:
            spider.logger.info('Time transcurred: %s', (datetime.now() - spider.start_time).total_seconds())
            spider.logger.info('%s returned for request to %s', response.status, request.url)
            if not spider.access_token == request.headers['Authorization'] and self._expires_soon(spider):
                # SAVE the last request to continue after getting the token
                spider.last_request = request
                # spider MUST implement the request_access_token method
                return spider.request_access_token()
            request.headers['Authorization'] = spider.access_token
            return request
        return response

    @staticmethod
    def _expires_soon(spider):
        if spider.start_time and spider.access_token:
            # The spider must implement the expires_soon method.
            return spider.expires_soon(datetime.now() - spider.start_time)
        return True


class OpenOppsAuthMiddleware:
    """
    Downloader middleware that intercepts requests and adds the token for OpenOpps scraper.
    """

    @staticmethod
    def process_request(request, spider):
        if 'token_request' in request.meta and request.meta['token_request']:
            return
        request.headers['Authorization'] = spider.access_token


class KingfisherTransformBaseMiddleware:
    """
    Base class used by middlewares that corrects the packaging of OCDS data
    """
    def _split_data(self, spider, item, encoding='utf-8'):
        """
         If the item is a json lines file, yields each line, otherwise yields data back
        """
        if not spider.compressed_file_format == 'json_lines':
            yield item
        else:
            for number, line in enumerate(item, 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return
                if isinstance(line, bytes):
                    line = line.decode(encoding=encoding)
                yield line

    def _apply_root_path(self, items, spider):
        """
         If spider.root_path is set, calls ijson.items and yields each value, otherwise yields each item back
        """
        if not spider.root_path:
            yield from items
        else:
            for item in items:
                for number, parsed_item in enumerate(ijson.items(item, spider.root_path)):
                    # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                    if spider.sample and number > spider.sample:
                        return
                    yield parsed_item

    def _get_package_metadata(self, data, skip_key, data_type):
        """
        Returns the package metadata from a file object.

        :param data: a data object
        :param str skip_key: the key to skip
        :returns: the package metadata
        :rtype: dict
        """
        package = {}
        if 'package' in data_type:
            for item in util.items(ijson.parse(data), '', skip_key=skip_key):
                package.update(item)
        return package

    def _add_package(self, items, data_type, list_type):
        """
        If data_type is release or record, adds a simple package to each item, otherwise yields each item back
        """
        if data_type not in ('release', 'record'):
            yield from items
        else:
            package = {list_type: []}
            for item in items:
                if isinstance(item, dict):
                    package[list_type].append(item)
                else:
                    package[list_type].append(json.loads(item))
            yield package

    def _resize_package(self, list_data, package_data, data_type, spider, file_name, url, encoding, list_type):
        """
        Yield a release package or record package, with a maximum number of releases or records per package.
        Once Kingfisher Process can handle large files, we can remove this logic, which is only required for handling
        compressed_file_format = 'release_package'. https://github.com/open-contracting/kingfisher-collect/issues/154
        """
        max_releases_per_package = 100
        if spider.sample:
            size = spider.sample
        else:
            size = max_releases_per_package

        package = self._get_package_metadata(package_data, list_type, data_type)
        # We yield a release o record package with a maximum of self.max_releases_per_package releases or records
        for item in list_data:
            for number, items in enumerate(util.grouper(ijson.items(item, f'{list_type}.item'), size), 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return
                package[list_type] = filter(None, items)
                data = json.dumps(package, default=util.default)
                yield spider.build_file_item(number=number, file_name=file_name, url=url, data=data,
                                             data_type=data_type, encoding=encoding)

    def _get_list_type(self, data_type):
        """
        Returns if the packages contains a list of releases or records
        """
        if 'record' in data_type:
            list_type = 'records'
        else:
            list_type = 'releases'
        return list_type

    def _get_transformed_data_type(self, data_type):
        """
        Returns a valid OCDS data type: record_package or release_package
        """

        if 'package' in data_type:
            transformed_data_type = data_type
        else:
            transformed_data_type = f'{data_type}_package'

        return transformed_data_type


class KingfisherTransformCompressedMiddleware(KingfisherTransformBaseMiddleware):
    """
    Middleware that corrects the packaging of OCDS data (whether the OCDS data is embedded, line-delimited JSON, etc.).
    """
    def process_spider_output(self, response, result, spider):
        for item in result:

            if not(isinstance(item, File) and (isinstance(spider, CompressedFileSpider) or
                                               spider.compressed_file_format)):
                yield item
                continue

            if isinstance(spider, CompressedFileSpider):
                data = item['data']['data']
            else:
                data = item['data']

            data_type = item['data_type']
            list_type = self._get_list_type(data_type)
            # If it is a compressed file and the file does'nt need any transformation
            if spider.compressed_file_format is None:
                item['data'] = data.read()
                yield item

            else:
                items = self._split_data(spider, data, item['encoding'])
                items = self._apply_root_path(items, spider)
                items = self._add_package(items, data_type, list_type)
                data_type = self._get_transformed_data_type(data_type)
                if spider.compressed_file_format == 'json_lines':
                    for number, data in enumerate(items, 1):
                        yield spider.build_file_item(number=number, file_name=item['file_name'], url=item['url'],
                                                     data=data, data_type=data_type, encoding=item['encoding'])
                else:
                    package_data = item['data']['package']
                    yield from self._resize_package(items, package_data, data_type, spider, item['file_name'],
                                                    item['url'], item['encoding'], list_type)


class KingfisherTransformMiddleware(KingfisherTransformBaseMiddleware):
    """
    Middleware that corrects the packaging of OCDS data (whether the OCDS data is embedded, line-delimited JSON, etc.).
    """

    def process_spider_output(self, response, result, spider):
        for item in result:

            if not(isinstance(item, File) and (item['data_type'] not in ('release_package', 'record_package') or
                                               spider.root_path) and not isinstance(spider, CompressedFileSpider)):
                yield item
                continue

            data_type = item['data_type']
            list_type = self._get_list_type(data_type)
            items = self._apply_root_path([item['data']], spider)
            items = self._add_package(items, data_type, list_type)
            data_type = self._get_transformed_data_type(data_type)
            for number, data in enumerate(items, 1):
                data = json.dumps(data, default=util.default)
                yield spider.build_file_item(number=number, file_name=item['file_name'], url=item['url'], data=data,
                                             data_type=data_type, encoding=item['encoding'])
