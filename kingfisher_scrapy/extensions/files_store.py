import os

from scrapy import signals
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileItem


class FilesStore:
    """
    Writes items' data to individual files in a directory. See the :ref:`how-it-works` documentation.
    """

    def __init__(self, directory):
        self.directory = directory

    @classmethod
    def relative_crawl_directory(cls, spider):
        """
        Returns the crawl's relative directory, in the format `<spider_name>[_sample]/<YYMMDD_HHMMSS>`.
        """
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

        return extension

    def spider_opened(self, spider):
        if hasattr(spider, '_job'):
            path = os.path.join(self.relative_crawl_directory(spider), 'scrapyd-job.txt')
            self._write_file(path, spider._job)

    def item_scraped(self, item, spider):
        """
        If the item is a File or FileItem, writes its data to the filename in the crawl's directory.

        Returns a dict with the metadata.
        """
        if not isinstance(item, (File, FileItem)):
            return

        file_name = item['file_name']
        if isinstance(item, FileItem):
            name, extension = util.get_file_name_and_extension(file_name)
            file_name = f"{name}-{item['number']}.{extension}"

        path = os.path.join(self.relative_crawl_directory(spider), file_name)
        self._write_file(path, item['data'])

        item['path'] = path
        item['files_store'] = self.directory

    def _write_file(self, path, data):
        path = os.path.join(self.directory, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if isinstance(data, bytes):
            mode = 'wb'
        else:
            mode = 'w'

        with open(path, mode) as f:
            if isinstance(data, (bytes, str)):
                f.write(data)  # NOTE: should be UTF-8
            else:
                util.json_dump(data, f)
