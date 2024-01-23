from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import IncoherentConfigurationError
from kingfisher_scrapy.util import handle_http_error


class BigFileSpider(SimpleSpider):
    """
    This class makes it easy to collect data from a source that publishes very large packages. Each package is split
    into smaller packages, each containing 100 releases or records. Users can then process the files without using an
    iterative parser and without having memory issues.

    #. Inherit from ``BigFileSpider``
    #. Write a ``start_requests()`` method to request the archive files

    .. code-block:: python

        from kingfisher_scrapy.base_spiders import BigFileSpider
        from kingfisher_scrapy.util import components

        class MySpider(BigFileSpider):
            name = 'my_spider'

            def start_requests(self):
                yield self.build_request('https://example.com/api/package.json', formatter=components(-1)

    .. note::

       ``concatenated_json = True``, ``line_delimited = True`` and ``root_path`` are not supported, because this spider
       yields items whose ``data`` field has ``package`` and ``data`` keys.
    """

    resize_package = True

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BigFileSpider, cls).from_crawler(crawler, *args, **kwargs)

        if spider.data_type not in ('release_package', 'record_package'):
            raise IncoherentConfigurationError(
                f"data_type must be 'release_package' or 'record_package', not {spider.data_type!r}.")

        return spider

    @handle_http_error
    def parse(self, response):
        yield self.build_file(file_name=response.request.meta['file_name'], url=response.request.url,
                              data_type=self.data_type, data={'data': response.body, 'package': response.body})
