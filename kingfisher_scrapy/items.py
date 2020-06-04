# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy

from kingfisher_scrapy.exceptions import MissingRequiredFieldError


class KingfisherItem(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()

    def validate(self):
        """
        Raises an error if any required field is missing.

        :raises kingfisher_scrapy.extensions.MissingRequiredFieldError: if any required field is missing
        """
        if hasattr(self, 'required'):
            for field in self.required:
                if field not in self:
                    raise MissingRequiredFieldError(field)


class File(KingfisherItem):
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()

    # If a file is split into file items, the file is stored to disk, but not sent to Kingfisher Process.
    post_to_api = scrapy.Field()

    # Added by the KingfisherFilesStore extension, for the KingfisherProcessAPI extension to read the file.
    path = scrapy.Field()
    files_store = scrapy.Field()

    required = [
        'file_name',
        'url',
        'data',
        'data_type',
    ]


class FileItem(KingfisherItem):
    number = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()

    required = [
        'number',
        'file_name',
        'url',
        'data',
        'data_type',
    ]


class FileError(KingfisherItem):
    errors = scrapy.Field()
    required = [
        'file_name',
        'url',
        'errors',
    ]


class LatestReleaseDateItem(scrapy.Item):
    date = scrapy.Field()
