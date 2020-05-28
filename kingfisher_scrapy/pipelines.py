# https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# https://docs.scrapy.org/en/latest/topics/signals.html#item-signals


class KingfisherScrapyPipeline:
    def process_item(self, item, spider):
        item.validate()

        return item
