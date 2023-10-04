import copy
import json
from zipfile import BadZipFile

import ijson

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileItem

MAX_GROUP_SIZE = 100


# Avoid reading the rest of a large file, since the rest of the items will be dropped.
def sample_filled(spider, number):
    return spider.sample and number > spider.sample


def group_size(spider):
    if spider.sample:
        return min(spider.sample, MAX_GROUP_SIZE)
    return MAX_GROUP_SIZE


class ConcatenatedJSONMiddleware:
    """
    If the spider's ``concatenated_json`` class attribute is ``True``, yields each object of the File as a FileItem.
    Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        """
        :returns: a generator of FileItem objects, in which the ``data`` field is parsed JSON
        """
        for item in result:
            if not isinstance(item, File) or not spider.concatenated_json:
                yield item
                continue

            data = item['data']

            # ijson can read from bytes or a file-like object.
            for number, obj in enumerate(util.transcode(spider, ijson.items, data, '', multiple_values=True), 1):
                if sample_filled(spider, number):
                    return

                yield spider.build_file_item(number, obj, item)


class LineDelimitedMiddleware:
    """
    If the spider's ``line_delimited`` class attribute is ``True``, yields each line of the File as a FileItem.
    Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        """
        :returns: a generator of FileItem objects, in which the ``data`` field is bytes
        """
        for item in result:
            if not isinstance(item, File) or not spider.line_delimited:
                yield item
                continue

            data = item['data']
            # Data can be bytes or a file-like object.
            if isinstance(data, bytes):
                data = data.splitlines(True)

            for number, line in enumerate(data, 1):
                if sample_filled(spider, number):
                    return

                yield spider.build_file_item(number, line, item)


class RootPathMiddleware:
    """
    If the spider's ``root_path`` class attribute is non-empty, replaces the item's ``data`` with the objects at that
    prefix; if there are multiple releases, records or packages at that prefix, combines them into a single package,
    and updates the item's ``data_type`` if needed. Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        """
        :returns: a generator of File or FileItem objects, in which the ``data`` field is parsed JSON
        """
        for item in result:
            if not isinstance(item, (File, FileItem)) or not spider.root_path:
                yield item
                continue

            data = item['data']
            is_multiple = 'item' in spider.root_path.split('.')
            is_package = 'package' in item['data_type']

            if isinstance(data, (dict, list)):
                data = util.json_dumps(data).encode()

            if 'release' in item['data_type']:
                key = 'releases'
                data_type = 'release_package'
            else:
                key = 'records'
                data_type = 'record_package'

            package = {key: [], 'version': spider.ocds_version}

            for number, obj in enumerate(util.transcode(spider, ijson.items, data, spider.root_path), 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    break

                # Two common issues in OCDS data are:
                #
                # - Multiple releases or records, without a package
                # - Multiple packages in a single file (often with a single release, record or OCID per package)
                #
                # Yielding each release, record or package creates a lot of overhead in terms of the number of files
                # written, the number of messages in RabbitMQ and the number of rows in PostgreSQL.
                #
                # We fix the packaging to reduce the overhead.
                if is_multiple:
                    # Assume that the `extensions` are the same for all packages.
                    if number == 1 and is_package:
                        package = obj.copy()
                        package[key] = []

                    if is_package:
                        package[key].extend(obj[key])
                    else:
                        package[key].append(obj)
                else:
                    item['data'] = obj
                    yield item

            if is_multiple:
                item['data'] = package
                item['data_type'] = data_type
                yield item


class AddPackageMiddleware:
    """
    If the spider's ``data_type`` class attribute is "release" or "record", wraps the item's ``data`` in an appropriate
    package, and updates the item's ``data_type``. Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        """
        :returns: a generator of File or FileItem objects, in which the ``data`` field is parsed JSON
        """
        for item in result:
            if not isinstance(item, (File, FileItem)) or item['data_type'] not in ('release', 'record'):
                yield item
                continue

            data = item['data']
            if hasattr(data, 'read'):
                data = data.read()

            # If the spider's ``root_path`` class attribute is non-empty, then the JSON data is already parsed.
            if not isinstance(data, dict):
                data = json.loads(data)

            if item['data_type'] == 'release':
                key = 'releases'
            else:
                key = 'records'

            item['data'] = {key: [data], 'version': spider.ocds_version}
            item['data_type'] += '_package'

            yield item


class ResizePackageMiddleware:
    """
    If the spider's ``resize_package`` class attribute is ``True``, splits the package into packages of 100 releases or
    records each. Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        """
        The spider must yield items whose ``data`` field has ``package`` and ``data`` keys.

        :returns: a generator of FileItem objects, in which the ``data`` field is a string
        """
        for item in result:
            if not isinstance(item, File) or not getattr(spider, 'resize_package', False):
                yield item
                continue

            data = item['data']

            if item['data_type'] == 'release_package':
                key = 'releases'
            else:
                key = 'records'

            package = self._get_package_metadata(spider, data['package'], key, item['data_type'])
            iterable = util.transcode(spider, ijson.items, data['data'], f'{key}.item')
            for number, items in enumerate(util.grouper(iterable, group_size(spider)), 1):
                if sample_filled(spider, number):
                    return

                data = copy.deepcopy(package)
                # Omit the None values returned by `grouper(*, fillvalue=None)`.
                data[key] = list(filter(None, items))

                yield spider.build_file_item(number, data, item)

    def _get_package_metadata(self, spider, data, skip_key, data_type):
        """
        Returns the package metadata from a file object.

        :param data: a data object
        :param str skip_key: the key to skip
        :returns: the package metadata
        :rtype: dict
        """
        package = {}
        if 'package' in data_type:
            for item in util.items(util.transcode(spider, ijson.parse, data), '', skip_key=skip_key):
                package.update(item)
        return package


class ReadDataMiddleware:
    """
    If the item's ``data`` is a file descriptor, replaces the item's ``data`` with the file's contents and closes the
    file descriptor. Otherwise, yields the original item.

    .. seealso::

       :class:`~kingfisher_scrapy.base_spiders.compressed_file_spider.CompressedFileSpider`
    """
    def process_spider_output(self, response, result, spider):
        """
        :returns: a generator of File objects, in which the ``data`` field is bytes
        """
        for item in result:
            if not isinstance(item, File) or not hasattr(item['data'], 'read'):
                yield item
                continue

            data = item['data'].read()
            item['data'].close()
            item['data'] = data
            yield item


class RetryDataErrorMiddleware:
    """
    Retries a request for a ZIP file up to 3 times, on the assumption that, if the spider raises a ``BadZipFile``
    exception, then the response was truncated.
    """
    # https://docs.scrapy.org/en/latest/topics/spider-middleware.html#scrapy.spidermiddlewares.SpiderMiddleware.process_spider_exception

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, BadZipFile):
            attempts = response.request.meta.get('retries', 0) + 1
            if attempts > 3:
                spider.logger.error('Gave up retrying %(request)s (failed %(failures)d times): %(exception)s',
                                    {'request': response.request, 'failures': attempts, 'exception': exception})
                return
            request = response.request.copy()
            request.dont_filter = True
            request.meta['retries'] = attempts
            spider.logger.debug('Retrying %(request)s (failed %(failures)d times): %(exception)s',
                                {'request': response.request, 'failures': attempts, 'exception': exception})
            yield request
        else:
            raise exception
