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


class KingfisherTransformMiddleware:
    """
    Middleware that corrects the packaging of OCDS data (whether the OCDS data is embedded, line-delimited JSON, etc.).
    """
    MAX_RELEASES_PER_PACKAGE = 100

    def process_spider_output(self, response, result, spider):
        for item in result:

            if not(isinstance(item, File) and (spider.data_type not in ('release_package', 'record_package') or
                                               isinstance(spider, CompressedFileSpider)) or spider.file_format):
                yield item
                continue
            kwargs = {
                'file_name': item['file_name'],
                'url': response.request.url,
                'data_type': item['data_type'],
                'encoding': item['encoding'],
            }

            if isinstance(spider, CompressedFileSpider):
                data = item['data']['data']
                package = item['data']['package']
                compressed_file = True
            else:
                data = item['data']
                package = item['data']
                compressed_file = False
            # if it is a compressed file and the file does'nt need any transformation
            if compressed_file and spider.compressed_file_format is None:
                item['data'] = data.read()
                yield item
            # if it is a compressed file or regular file but as json_lines
            elif spider.file_format or (compressed_file and spider.compressed_file_format == 'json_lines'):
                yield from self._parse_json_lines(spider, data, **kwargs)
            # otherwise is must be a release or record package or a list of them
            else:
                yield from self._parse_json_array(spider, package, data, **kwargs)

    def _parse_json_array(self, spider, package_data, list_data, *, file_name='data.json', url=None, data_type=None,
                          encoding='utf-8'):

        if 'record' in data_type:
            list_type = 'records'
        else:
            list_type = 'releases'

        package = self._get_package_metadata(package_data, list_type, data_type, spider.root_path)
        # we change the data_type into a valid one:release_package or record_package
        if data_type in ('release', 'record'):
            data_type = f'{data_type}_package'

        # we yield a release o record package with a maximum of self.MAX_RELEASES_PER_PACKAGE releases or records
        for number, items in enumerate(util.grouper(ijson.items(list_data, spider.root_path),
                                                    self.MAX_RELEASES_PER_PACKAGE), 1):
            package[list_type] = filter(None, items)
            data = json.dumps(package, default=util.default)
            yield spider.build_file_item(number=number, file_name=file_name, url=url, data=data,
                                         data_type=data_type, encoding=encoding)

    def _parse_json_lines(self, spider, data, *, file_name='data.json', url=None, data_type=None, encoding='utf-8'):
        for number, line in enumerate(data, 1):
            if isinstance(line, bytes):
                line = line.decode(encoding=encoding)
            yield from self._parse_json_array(spider, line, line, file_name=file_name, url=url, data_type=data_type,
                                              encoding=encoding)
            return

    def _get_package_metadata(self, data, skip_key, data_type, root_path):
        """
        Returns the package metadata from a file object.

        :param data: a data object
        :param str skip_key: the key to skip
        :returns: the package metadata
        :rtype: dict
        """
        package = {}
        if 'package' in data_type:
            for item in util.items(ijson.parse(data), root_path, skip_key=skip_key):
                package.update(item)
        return package
