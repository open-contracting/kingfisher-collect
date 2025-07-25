import copy
import json
from zipfile import BadZipFile

import ijson
from scrapy.exceptions import DropItem
from scrapy.utils.log import logformatter_adapter

from kingfisher_scrapy import util
from kingfisher_scrapy.exceptions import RetryableError
from kingfisher_scrapy.items import File, FileItem

MAX_GROUP_SIZE = 100


# Avoid reading the rest of a large file, since the rest of the items will be dropped.
def sample_filled(spider, number):
    return spider.sample and number > spider.sample


def group_size(spider):
    if spider.sample:
        return min(spider.sample, MAX_GROUP_SIZE)
    return MAX_GROUP_SIZE


def read_data_from_file_if_any(item):
    if hasattr(item.data, "read"):
        content = item.data.read()
        item.data.close()
        item.data = content


class ConcatenatedJSONMiddleware:
    """
    If the spider's ``concatenated_json`` class attribute is ``True``, yield each object of the File as a FileItem.
    Otherwise, yield the original item.
    """

    async def process_spider_output(self, response, result, spider):
        """Return a generator of FileItem objects, in which the ``data`` field is parsed JSON."""
        async for item in result:
            if not spider.concatenated_json or not isinstance(item, File):
                yield item
                continue

            data = item.data

            # ijson can read from bytes or a file-like object.
            for number, obj in enumerate(util.transcode(spider, ijson.items, data, "", multiple_values=True), 1):
                if sample_filled(spider, number):
                    return

                yield spider.build_file_item(number, obj, item)


class LineDelimitedMiddleware:
    """
    If the spider's ``line_delimited`` class attribute is ``True``, yield each line of the File as a FileItem.
    Otherwise, yield the original item.
    """

    async def process_spider_output(self, response, result, spider):
        """Return a generator of FileItem objects, in which the ``data`` field is bytes."""
        async for item in result:
            if not spider.line_delimited or not isinstance(item, File):
                yield item
                continue

            data = item.data
            # Data can be bytes or a file-like object. If bytes, split into an iterable.
            if isinstance(data, bytes):
                data = data.splitlines(keepends=True)

            for number, line in enumerate(data, 1):
                if sample_filled(spider, number):
                    return

                yield spider.build_file_item(number, line, item)


class ValidateJSONMiddleware:
    """
    If the spider's ``validate_json`` class attribute is ``True``,  check if the item's ``data`` field is valid
    JSON. If not, yield nothing. Otherwise, yield the original item.
    """

    async def process_spider_output(self, response, result, spider):
        """Return a generator of File or FileItem objects, in which the ``data`` field is valid JSON."""
        async for item in result:
            if not spider.validate_json or not isinstance(item, File | FileItem) or isinstance(item.data, dict):
                yield item
                continue

            read_data_from_file_if_any(item)

            try:
                json.loads(item.data)

                yield item
            except json.JSONDecodeError:
                spider.crawler.stats.inc_value("invalid_json_count")
                # https://github.com/scrapy/scrapy/blob/48c5a8c/scrapy/core/scraper.py#L364-L367
                logkws = spider.crawler.logformatter.dropped(item, DropItem("Invalid JSON"), response, spider)
                if logkws is not None:
                    spider.logger.log(*logformatter_adapter(logkws), extra={"spider": spider})


class RootPathMiddleware:
    """
    If the spider's ``root_path`` class attribute is non-empty, replace the item's ``data`` with the objects at that
    prefix; if there are multiple releases, records or packages at that prefix, combine them into packages in groups
    of 100, and update the item's ``data_type`` if needed. Otherwise, yield the original item.
    """

    async def process_spider_output(self, response, result, spider):
        """Return a generator of File or FileItem objects, in which the ``data`` field is parsed JSON."""
        async for item in result:
            if not spider.root_path or not isinstance(item, File | FileItem):
                yield item
                continue

            data = item.data
            # Re-encode the data, to traverse the JSON using only ijson, instead of either ijson or Python.
            # This is only expected to occur when both `root_path` and `concatenated_json` are set.
            if isinstance(data, dict):
                data = util.json_dumps(data).encode()

            iterable = util.transcode(spider, ijson.items, data, spider.root_path)

            if "item" in spider.root_path.split("."):
                # Two common issues in OCDS data are:
                #
                # - Multiple releases or records, without a package
                # - Multiple packages in a single file (often with a single release, record or OCID per package)
                #
                # Yielding each release, record or package creates a lot of overhead in terms of the number of files
                # written, the number of messages in RabbitMQ and the number of rows in PostgreSQL.
                #
                # We re-package in groups of 100 to reduce the overhead.

                is_package = "package" in item.data_type

                if "release" in item.data_type:
                    key = "releases"
                    item.data_type = "release_package"
                else:
                    key = "records"
                    item.data_type = "record_package"

                for number, items in enumerate(util.grouper(iterable, group_size(spider)), 1):
                    if sample_filled(spider, number):
                        return

                    # Omit the None values returned by `grouper(*, fillvalue=None)`.
                    items = filter(None, items)

                    if is_package:
                        # Assume that the `extensions` are the same for all packages.
                        package = next(items)
                        try:
                            releases_or_records = package[key]
                        except KeyError as e:
                            spider.logger.warning("%(key)s not set in %(data)r", {"key": e, "data": package})
                        for other in items:
                            try:
                                releases_or_records.extend(other[key])
                            except KeyError as e:
                                spider.logger.warning("%(key)s not set in %(data)r", {"key": e, "data": other})
                    else:
                        package = {"version": spider.ocds_version, key: list(items)}

                    yield spider.build_file_item(number, package, item)
            else:
                # Iterates at most once.
                for number, obj in enumerate(iterable, 1):
                    if sample_filled(spider, number):
                        return

                    item.data = obj

                    yield item


class AddPackageMiddleware:
    """
    If the spider's ``data_type`` class attribute is "release" or "record", wrap the item's ``data`` in an appropriate
    package, and update the item's ``data_type``. Otherwise, yield the original item.
    """

    async def process_spider_output(self, response, result, spider):
        """Return a generator of File or FileItem objects, in which the ``data`` field is parsed JSON."""
        async for item in result:
            if not isinstance(item, File | FileItem) or item.data_type not in {"release", "record"}:
                yield item
                continue

            read_data_from_file_if_any(item)

            data = item.data
            # If the spider's `root_path` class attribute is non-empty, then the JSON data is already parsed.
            if isinstance(data, bytes):
                data = json.loads(data)

            key = "releases" if item.data_type == "release" else "records"

            item.data = {"version": spider.ocds_version, key: [data]}
            item.data_type += "_package"

            yield item


class ResizePackageMiddleware:
    """
    If the spider's ``resize_package`` class attribute is ``True``, split the package into packages of 100 releases or
    records each. Otherwise, yield the original item.

    Optionally, implement an ``ocid_fallback`` method on the spider, which accepts a release (or record) and returns an
    an ``ocid`` value, to be used if the ``ocid`` field is not set.
    """

    async def process_spider_output(self, response, result, spider):
        """
        Return a generator of FileItem objects, in which the ``data`` field is a string.

        The spider must yield items whose ``data`` field has ``package`` and ``data`` keys.
        """
        async for item in result:
            if not spider.resize_package or not isinstance(item, File):
                yield item
                continue

            data = item.data

            key = "releases" if item.data_type == "release_package" else "records"

            template = self._get_package_metadata(spider, data["package"], key, item.data_type)
            iterable = util.transcode(spider, ijson.items, data["data"], f"{key}.item")

            for number, items in enumerate(util.grouper(iterable, group_size(spider)), 1):
                if sample_filled(spider, number):
                    return

                # Kingfisher Process merges only releases and records with OCIDs.
                if hasattr(spider, "ocid_fallback"):
                    for entry in items:
                        if entry and "ocid" not in entry:
                            entry["ocid"] = spider.ocid_fallback(entry)

                package = copy.deepcopy(template)
                # Omit the None values returned by `grouper(*, fillvalue=None)`.
                package[key] = list(filter(None, items))

                yield spider.build_file_item(number, package, item)

    def _get_package_metadata(self, spider, data, skip_key, data_type):
        """
        Return the package metadata from a file object.

        :param data: a data object
        :param str skip_key: the key to skip
        :returns: the package metadata
        :rtype: dict
        """
        package = {}
        if "package" in data_type:
            for item in util.items(util.transcode(spider, ijson.parse, data), "", skip_key=skip_key):
                package.update(item)
        return package


class ReadDataMiddleware:
    """
    If the item's ``data`` is a file descriptor, replace the item's ``data`` with the file's contents and close the
    file descriptor. Otherwise, yield the original item.

    .. seealso::

       :class:`~kingfisher_scrapy.base_spiders.compressed_file_spider.CompressedFileSpider`
    """

    async def process_spider_output(self, response, result, spider):
        """Return a generator of File objects, in which the ``data`` field is bytes."""
        async for item in result:
            if not isinstance(item, File) or not hasattr(item.data, "read"):
                yield item
                continue

            read_data_from_file_if_any(item)

            yield item


class RetryDataErrorMiddleware:
    """
    Retry a request up to 3 times.

    Either when the spider raises a ``BadZipFile`` exception, on the assumption that the response was truncated,
    or when the spider raises a ``RetryableError`` exception.
    """

    # https://docs.scrapy.org/en/latest/topics/spider-middleware.html#scrapy.spidermiddlewares.SpiderMiddleware.process_spider_exception

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, BadZipFile | RetryableError):
            attempts = response.request.meta.get("retries", 0) + 1
            if attempts > 3:
                spider.logger.error(
                    "Gave up retrying %(request)s (failed %(failures)d times): %(exception)s",
                    {"request": response.request, "failures": attempts, "exception": exception},
                )
                return
            request = response.request.copy()
            request.dont_filter = True
            request.meta["retries"] = attempts
            spider.logger.debug(
                "Retrying %(request)s (failed %(failures)d times): %(exception)s",
                {"request": response.request, "failures": attempts, "exception": exception},
            )
            yield request
        else:
            raise exception
