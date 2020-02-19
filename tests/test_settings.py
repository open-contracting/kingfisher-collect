import kingfisher_scrapy.settings


class TestSettings():
    name = 'test'
    both_name = kingfisher_scrapy.settings.BOT_NAME
    assert both_name == kingfisher_scrapy.settings.BOT_NAME
