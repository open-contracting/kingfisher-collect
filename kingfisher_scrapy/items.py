import scrapy


class File(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()

    # If a file is split into file items, the file is stored to disk, but not sent to Kingfisher Process.
    post_to_api = scrapy.Field()

    # Added by the KingfisherFilesStore extension, for the KingfisherProcessAPI extension to read the file.
    path = scrapy.Field()
    files_store = scrapy.Field()


class FileItem(scrapy.Item):
    number = scrapy.Field()
    file_name = scrapy.Field()
    url = scrapy.Field()
    data = scrapy.Field()
    data_type = scrapy.Field()
    encoding = scrapy.Field()


class FileError(scrapy.Item):
    file_name = scrapy.Field()
    url = scrapy.Field()
    errors = scrapy.Field()


class LastReleaseDate(scrapy.Item):
    date = scrapy.Field()
