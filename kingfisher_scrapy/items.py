import scrapy


class File(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()
    post_to_api = scrapy.Field()

    # Added by extensions.
    path = scrapy.Field()
    files_store = scrapy.Field()


class FileItem(scrapy.Item):
    number = scrapy.Field()
    file_name = scrapy.Field()
    url = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()
    post_to_api = scrapy.Field()


class FileError(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()
    errors = scrapy.Field()
