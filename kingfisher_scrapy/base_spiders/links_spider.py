from jsonpointer import resolve_pointer

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import MissingNextLinkError
from kingfisher_scrapy.util import handle_http_error


class LinksSpider(SimpleSpider):
    """
    Collect data from an API that implements the `pagination
    <https://github.com/open-contracting-extensions/ocds_pagination_extension>`__ pattern.

    #. Inherit from ``LinksSpider``
    #. Set a ``data_type`` class attribute to the data type of the API responses
    #. Set a ``formatter`` class attribute to set the file name like in
       :meth:`~kingfisher_scrapy.base_spiders.BaseSpider.build_request`
    #. Set a ``next_link_formatter`` class attribute if pagination URLs differ from start URLs
    #. Write a ``start_requests()`` method to request the first page of API results
    #. Optionally, set a ``next_pointer`` class attribute to the JSON Pointer for the next link (default "/links/next")

    If the API returns the number of total pages or results in the response, consider using ``IndexSpider`` instead.

    .. code-block:: python

        import scrapy

        from kingfisher_scrapy.base_spiders import LinksSpider

        class MySpider(LinksSpider):
            name = 'my_spider'

            # SimpleSpider
            data_type = 'release_package'

            # LinksSpider
            formatter = staticmethod(parameters('page'))

            def start_requests(self):
                yield scrapy.Request('https://example.com/api/packages.json', meta={'file_name': 'page-1.json'})

    """

    next_pointer = '/links/next'

    @handle_http_error
    def parse(self, response):
        yield from super().parse(response)

        yield self.next_link(response)

    def next_link(self, response, **kwargs):
        """If the JSON response has a ``links.next`` key, returns a ``scrapy.Request`` for the URL."""
        # If the sample size is 1, we don't want to parse the response, especially if --max-bytes is used.
        if self.sample and self.sample == 1:
            return None

        data = response.json()
        url = resolve_pointer(data, self.next_pointer, None)
        if url:
            return self.build_request(url, formatter=getattr(self, "next_link_formatter", self.formatter), **kwargs)

        for filter_argument in self.filter_arguments:
            if getattr(self, filter_argument, None):
                return None

        if response.meta['depth'] == 0:
            raise MissingNextLinkError(f'next link not found on the first page: {response.url}')

        return None
