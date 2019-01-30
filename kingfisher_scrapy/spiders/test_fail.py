import scrapy


class TestFail(scrapy.Spider):
    name = "test_fail"
    start_urls = ['https://www.open-contracting.org']

    def parse(self, response):
        urls = [
            'https://raw.githubusercontent.com/open-contracting/sample-data/master/fictional-example/1.1/ocds-213czf-000-00001-01-planning.json',  # noqa # Fine
            'https://www.open-contracting.org/i-want-a-kitten',  # A straight 404
            'http://httpstat.us/500',  # I broke the server ....
            'http://httpstat.us/502',  # .... but actually, yes, I also broke the Proxy too
        ]
        for url in urls:
            yield {
                "file_urls": [url],
                "data_type": "release_package"
            }
