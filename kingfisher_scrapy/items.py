# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()
    validate = True

    # Added by the CheckJSONFormat middleware, for the Validate pipeline to drop the item if invalid.
    invalid_format = scrapy.Field()


class File(Item):
    data = scrapy.Field()
    data_type = scrapy.Field()

    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path = scrapy.Field()


class FileItem(Item):
    number = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()

    # Added by the FilesStore extension, for the KingfisherProcessAPI2 extension to refer to the file.
    path = scrapy.Field()


class FileError(Item):
    errors = scrapy.Field()


class PluckedItem(scrapy.Item):
    value = scrapy.Field()
