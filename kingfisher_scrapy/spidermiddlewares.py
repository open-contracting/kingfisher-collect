import json

import ijson

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileItem


class ConcatenatedJSONMiddleware:
    """
    If the spider's ``concatenated_json`` class attribute is ``True``, yields each object of the File as a FileItem.
    Otherwise, yields the original item.
    """
    def process_spider_output(self, response, result, spider):
        for item in result:
            if not isinstance(item, File) or not spider.concatenated_json:
                yield item
                continue

            data = item['data']
            for number, obj in enumerate(ijson.items(data, '', multiple_values=True), 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return

                yield spider.build_file_item(number, obj, item)


class LineDelimitedMiddleware:
    """
    If the spider's ``line_delimited`` class attribute is ``True``, yields each line of the File as a FileItem.
    Otherwise, yields the original item.
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

                yield spider.build_file_item(number, line, item)


class RootPathMiddleware:
    """
    If the spider's ``root_path`` class attribute is non-empty, yields a FileItem for each object at that prefix.
    Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        for item in result:
            if not isinstance(item, (File, FileItem)) or not spider.root_path:
                yield item
                continue

            data = item['data']

            for number, obj in enumerate(ijson.items(data, spider.root_path), 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return

                if isinstance(item, File):
                    yield spider.build_file_item(number, obj, item)
                else:
                    # If the JSON file is line-delimited and the root path is to a JSON array, then this method will
                    # need to yield multiple FileItems for each input FileItem. To do so, the input FileItem's number
                    # is multiplied by the maximum length of the JSON array, to avoid duplicate numbers. Note that, to
                    # be stored by Kingfisher Process, the number must be within PostgreSQL's integer range.
                    #
                    # If this is the case, then, on the spider, set a ``root_path_max_length`` class attribute to the
                    # maximum length of the JSON array at the root path.
                    #
                    # https://www.postgresql.org/docs/11/datatype-numeric.html
                    yield spider.build_file_item((item['number'] - 1) * spider.root_path_max_length + number,
                                                 obj, item)


class AddPackageMiddleware:
    """
    If the spider's ``data_type`` class attribute is "release" or "record", wraps the data in a package.
    Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        for item in result:
            if not isinstance(item, (File, FileItem)) or item['data_type'] not in ('release', 'record'):
                yield item
                continue

            data = item['data']

            # If the spider's ``root_path`` class attribute is non-empty, then the JSON data is already parsed.
            if not isinstance(data, dict):
                data = json.loads(data, encoding=item['encoding'])

            if item['data_type'] == 'release':
                key = 'releases'
            else:
                key = 'records'
            item['data'] = {key: [data], 'version': spider.ocds_version}
            item['data_type'] += '_package'

            yield item


class ResizePackageMiddleware:
    """
    If the spider's ``resize_package`` class attribute is ``True``, splits the package into multiple packages.
    Otherwise, yields the original item.
    """

    def process_spider_output(self, response, result, spider):
        for item in result:
            if not isinstance(item, File) or not getattr(spider, 'resize_package', False):
                yield item
                continue

            if spider.sample:
                size = spider.sample
            else:
                size = 100

            package = self._get_package_metadata(item['data']['package'], 'releases', item['data_type'])
            # We yield release packages containing a maximum of 100 releases.
            for number, items in enumerate(util.grouper(ijson.items(item['data']['data'], 'releases.item'), size), 1):
                # Avoid reading the rest of a large file, since the rest of the items will be dropped.
                if spider.sample and number > spider.sample:
                    return

                package['releases'] = filter(None, items)
                data = json.dumps(package, default=util.default)

                yield spider.build_file_item(number, data, item)

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


class ReadDataMiddleware:
    """
    If the item's ``data`` value is a file pointer, reads it.
    Otherwise, yields the original item.
    """
    def process_spider_output(self, response, result, spider):
        for item in result:
            if not isinstance(item, File) or not hasattr(item['data'], 'read'):
                yield item
                continue
            data = item['data'].read()
            item['data'].close()
            item['data'] = data
            yield item