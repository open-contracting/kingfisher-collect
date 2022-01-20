import os
from io import BytesIO
from zipfile import ZipFile

from rarfile import RarFile

from kingfisher_scrapy.base_spiders.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import UnknownArchiveFormatError
from kingfisher_scrapy.items import File
from kingfisher_scrapy.util import get_file_name_and_extension, handle_http_error


class CompressedFileSpider(BaseSpider):
    """
    This class makes it easy to collect data from ZIP or RAR files. It assumes all files have the same data type.
    Each compressed file is saved to disk. The archive file is *not* saved to disk.

    #. Inherit from ``CompressedFileSpider``
    #. Set a ``data_type`` class attribute to the data type of the compressed files
    #. Optionally, add a ``resize_package = True`` class attribute to split large packages (e.g. greater than 100MB)
    #. Write a ``start_requests`` method to request the archive files

    .. code-block:: python

        from kingfisher_scrapy.base_spiders.compressed_file_spider import CompressedFileSpider
        from kingfisher_scrapy.util import components

        class MySpider(CompressedFileSpider):
            name = 'my_spider'

            # CompressedFileSpider
            data_type = 'release_package'

            def start_requests(self):
                yield self.build_request('https://example.com/api/packages.zip', formatter=components(-1))

    .. note::

       ``concatenated_json = True``, ``line_delimited = True``, ``root_path``, ``data_type = 'release'`` and
       ``data_type = 'record'`` are not supported if ``resize_package = True``.
    """

    # BaseSpider
    dont_truncate = True

    resize_package = False
    file_name_must_contain = ''

    @handle_http_error
    def parse(self, response):
        archive_name, archive_format = get_file_name_and_extension(response.request.meta['file_name'])

        if archive_format == 'zip':
            cls = ZipFile
        elif archive_format == 'rar':
            cls = RarFile
        else:
            raise UnknownArchiveFormatError(response.request.meta['file_name'])

        # If we use a context manager here, the archive file might close before the item pipeline reads from the file
        # handlers of the compressed files.
        archive_file = cls(BytesIO(response.body))

        number = 1
        for file_info in archive_file.infolist():
            # Avoid reading the rest of a large file, since the rest of the items will be dropped.
            if self.sample and number > self.sample:
                break

            filename = file_info.filename
            basename = os.path.basename(filename)
            if self.file_name_must_contain not in basename:
                continue
            if archive_format == 'rar' and file_info.isdir():
                continue
            if archive_format == 'zip' and file_info.is_dir():
                continue
            if not basename.endswith('.json'):
                basename += '.json'

            compressed_file = archive_file.open(filename)

            # If `resize_package = True`, then we need to open the file twice: once to extract the package metadata and
            # then to extract the releases themselves.
            if self.resize_package:
                data = {'data': compressed_file, 'package': archive_file.open(filename)}
            else:
                data = compressed_file

            yield File({
                'file_name': f'{archive_name}-{basename}',
                'data': data,
                'data_type': self.data_type,
                'url': response.request.url,
            })

            number += 1
