from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.util import handle_http_error


class SimpleSpider(BaseSpider):
    """
    Most spiders can inherit from this class.

    It assumes all responses have the same data type.

    #. Inherit from ``SimpleSpider``
    #. Set a ``data_type`` class attribute to the data type of the responses
    #. Write a ``start_requests()`` method (and any intermediate callbacks) to send requests

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spiders import SimpleSpider

        class MySpider(SimpleSpider):
            name = 'my_spider'

            # SimpleSpider
            data_type = 'release_package'

            def start_requests(self):
                yield scrapy.Request('https://example.com/api/package.json', meta={'file_name': 'all.json'})
    """

    @handle_http_error
    def parse(self, response):
        yield self.build_file_from_response(response, data_type=self.data_type)
