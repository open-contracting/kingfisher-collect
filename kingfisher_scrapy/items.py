# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()
    validate = True


class File(Item):
    data = scrapy.Field()
    data_type = scrapy.Field()

    # Added by the FilesStore extension, for the KingfisherProcessAPI extension to read the file.
    path = scrapy.Field()
    files_store = scrapy.Field()


class FileItem(Item):
    number = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()

    # Added by the FilesStore extension, for the KingfisherProcessAPI extension to read the file.
    path = scrapy.Field()
    files_store = scrapy.Field()


class FileError(Item):
    errors = scrapy.Field()


class PluckedItem(scrapy.Item):
    value = scrapy.Field()
