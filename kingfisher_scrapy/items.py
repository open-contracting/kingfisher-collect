# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KingfisherItem(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()
    validate = True


class File(KingfisherItem):
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()

    # Added by the KingfisherFilesStore extension, for the KingfisherProcessAPI extension to read the file.
    path = scrapy.Field()
    files_store = scrapy.Field()


class FileItem(KingfisherItem):
    number = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()

    # Added by the KingfisherFilesStore extension, for the KingfisherProcessAPI extension to read the file.
    path = scrapy.Field()
    files_store = scrapy.Field()


class FileError(KingfisherItem):
    errors = scrapy.Field()


class PluckedItem(scrapy.Item):
    value = scrapy.Field()
