# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
from datetime import datetime

import ijson
import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileItem


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


class KingfisherTransformLineDelimitedJSONMiddleware:
    """
    If the item is a line-delimited JSON file, yields each line. Otherwise, yields the item.
    """
    def process_spider_output(self, response, result, spider):
        for item in result:
            if not isinstance(item, File) or not spider.line_delimited:
                yield item
                continue

            data = item['data']
            # Data can be bytes or a file-like object.
            if isinstance(data, bytes):
                data = data.decode(encoding=item['encoding']).splitlines(True)

            for number, line in enumerate(data, 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return

                if isinstance(line, bytes):
                    line = line.decode(encoding=item['encoding'])

                yield FileItem({
                    'number': number,
                    'file_name': item['file_name'],
                    'data': line,
                    'data_type': item['data_type'],
                    'url': item['url'],
                    'encoding': item['encoding'],
                })


class KingfisherTransformRootPathMiddleware:
    """
    If spider.root_path is set, calls ijson.items and yields each value, otherwise yields each item back
    """
    def process_spider_output(self, response, result, spider):
        for item in result:
            if not isinstance(item, (File, FileItem)) or not spider.root_path:
                yield item
                continue

            data = item['data']
            for number, parsed_item in enumerate(ijson.items(data, spider.root_path)):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return

                item['data'] = parsed_item
                yield item


class KingfisherTransformAddPackageMiddleware:
    """
    If data_type is release or record, adds a simple package to each item, otherwise yields each item back
    """
    def process_spider_output(self, response, result, spider):
        for item in result:
            if not(isinstance(item, (File, FileItem)) and item['data_type'] in ('release', 'record')):
                yield item
                continue
            data = item['data']
            data_type = item['data_type']
            list_type = self._get_list_type(data_type)
            package = {list_type: []}
            if isinstance(data, dict):
                package[list_type].append(data)
            else:
                package[list_type].append(json.loads(data, encoding=item['encoding']))
            item['data'] = package
            item['data_type'] = f'{data_type}_package'
            yield item

    def _get_list_type(self, data_type):
        """
        Returns if the packages contains a list of releases or records
        """
        if 'record' in data_type:
            list_type = 'records'
        else:
            list_type = 'releases'
        return list_type


class KingfisherTransformResizePackageMiddleware:
    """
     If spider.root_path is set, calls ijson.items and yields each value, otherwise yields each item back
    """
    def process_spider_output(self, response, result, spider):
        for item in result:
            if not(isinstance(item, File) and hasattr(spider, 'compressed_file_format') and
                   spider.compressed_file_format == 'release_package'):
                yield item
                continue
            list_data = item['data']['data']
            package_data = item['data']['package']
            data_type = item['data_type']
            max_releases_per_package = 100
            if spider.sample:
                size = spider.sample
            else:
                size = max_releases_per_package

            package = self._get_package_metadata(package_data, 'releases', data_type)
            # We yield a release o record package with a maximum of self.max_releases_per_package releases or records
            for number, items in enumerate(util.grouper(ijson.items(list_data, 'releases.item'), size), 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return
                package['releases'] = filter(None, items)
                data = json.dumps(package, default=util.default)
                yield FileItem({
                    'number': number,
                    'file_name': item['file_name'],
                    'data': data,
                    'data_type': data_type,
                    'url': item['url'],
                    'encoding': item['encoding'],
                })

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
