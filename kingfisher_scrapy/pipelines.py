# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals
import json

from kingfisher_scrapy.items import FileItem, File, LastReleaseDate


class KingfisherScrapyPipeline:
    def process_item(self, item, spider):
        item.validate()

        return item


class LastReleaseDatePipeline:
    def process_item(self, item, spider):
        if spider.last and (isinstance(item, FileItem) or isinstance(item, File)):
            if item['data_type'] == 'release_package'\
                    or item['data_type'] == 'record_package':
                return LastReleaseDate({
                    'date': json.loads(item['data'])['releases'][0]['date']
                })
