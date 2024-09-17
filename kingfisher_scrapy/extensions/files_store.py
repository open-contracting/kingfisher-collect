import math
import os
import zlib

from scrapy import signals
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileItem


class FilesStore:
    """Write items' data to individual files in a directory. See the :ref:`how-it-works` documentation."""

    def __init__(self, directory):
        self.directory = directory

    @classmethod
    def relative_crawl_directory(cls, spider):
        """Return the crawl's relative directory, in the format `<spider_name>[_sample]/<YYMMDD_HHMMSS>`."""
        spider_directory = spider.name
        if spider.sample:
            spider_directory += '_sample'

        return os.path.join(spider_directory, spider.get_start_time('%Y%m%d_%H%M%S'))

    @classmethod
    def from_crawler(cls, crawler):
        directory = crawler.settings['FILES_STORE']

        if not directory:
            raise NotConfigured('FILES_STORE is not set.')

        extension = cls(directory)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def spider_opened(self, spider):
        if hasattr(spider, '_job'):
            path = os.path.join(self.relative_crawl_directory(spider), 'scrapyd-job.txt')
            self._write_file(path, spider._job)

    def spider_closed(self, spider, reason):
        if reason not in ('finished', 'sample') or spider.pluck:
            return

        path = os.path.join(self.directory, self.relative_crawl_directory(spider))

        if os.path.exists(path):
            message = f'The data is available at: {path}'
        else:
            message = 'Something went wrong. No data was downloaded.'
        message_length = math.ceil(len(message) / 2) * 2
        title_length = message_length // 2 - 8

        spider.logger.info(f"+-{'-' * title_length} DATA DIRECTORY {'-' * title_length}-+")  # noqa: G004
        spider.logger.info(f"| {' ' * message_length} |")  # noqa: G004
        spider.logger.info(f"| {message.ljust(message_length)} |")  # noqa: G004
        spider.logger.info(f"| {' ' * message_length} |")  # noqa: G004
        spider.logger.info(f"+-{'-' * message_length}-+")  # noqa: G004

    def item_scraped(self, item, spider):
        """
        If the item is a File or FileItem, write its data to the filename in a subdirectory of the crawl directory.

        Return a dict with the metadata.
        """
        if not isinstance(item, File | FileItem):
            return

        file_name = item.file_name
        if isinstance(item, FileItem):
            name, extension = util.get_file_name_and_extension(file_name)
            file_name = f"{name}-{item.number}.{extension}"

        path = os.path.join(self.relative_crawl_directory(spider), self._get_subdirectory(file_name), file_name)
        self._write_file(path, item.data)

        item.path = path

    # https://github.com/rails/rails/blob/05ed261/activesupport/lib/active_support/cache/file_store.rb#L150-L175
    @staticmethod
    def _get_subdirectory(file_name):
        checksum = zlib.adler32(file_name.encode())
        checksum, dir_1 = divmod(checksum, 0x1000)
        # 0x1000 is 4096, which should be sufficient, without another level of: dir_2 = checksum % 0x1000
        return f"{dir_1:03X}"

    def _write_file(self, path, data):
        path = os.path.join(self.directory, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        mode = 'wb' if isinstance(data, bytes) else 'w'

        with open(path, mode) as f:
            if isinstance(data, bytes | str):
                f.write(data)  # NOTE: should be UTF-8
            else:
                util.json_dump(data, f)
