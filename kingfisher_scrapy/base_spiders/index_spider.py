from math import ceil

from jsonpointer import resolve_pointer

from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import IncoherentConfigurationError
from kingfisher_scrapy.items import FileError
from kingfisher_scrapy.util import handle_http_error, parameters


class IndexSpider(SimpleSpider):
    """
    This class can be used to collect data from an API that includes the total number of results or pages in its
    response, and receives pagination parameters like ``page`` or ``limit`` and ``offset``. To create a spider that
    inherits from ``IndexSpider``:

    #. Set class attributes. Either:

        #. Set ``page_count_pointer`` to the JSON Pointer for the total number of pages in the first response. The
           spider then yields a request for each page, incrementing a ``page`` query string parameter in each request.
        #. Set ``result_count_pointer`` to the JSON Pointer for the total number of results, and set ``limit`` to the
           number of results to return per page, or to the JSON Pointer for it. Optionally, set ``use_page = True`` to
           configure the spider to send a ``page`` query string parameter instead of a pair of ``limit`` and ``offset``
           query string parameters. The spider then yields a request for each offset/page.

    #. If the ``page`` query string parameter is zero-indexed, set ``start_page = 0``.
    #. Set ``formatter`` to set the file name like in :meth:`~kingfisher_scrapy.base_spiders.BaseSpider.build_request`.
       If ``page_count_pointer`` or ``use_page = True``, it defaults to ``parameters(<param_page>)``. Otherwise, if
       ``result_count_pointer`` is set and ``use_page = False``, it defaults to ``parameters(<param_offset>)``. If
       ``formatter = None``, the ``url_builder()`` method must ``return url, {'meta': {'file_name': ...}, ...}``.
    #. Write a ``start_requests()`` method to yield the initial URL. The request's ``callback`` parameter should be set
       to ``self.parse_list``.

    If neither ``page_count_pointer`` nor ``result_count_pointer`` can be used to create the URLs (e.g. if you need to
    query a separate URL that does not return JSON), you need to define ``range_generator()`` and ``url_builder()``
    methods. ``range_generator()`` should return page numbers or offset numbers. ``url_builder()`` receives a page or
    offset from ``range_generator()``, and returns either a request URL, or a tuple of a request URL and keyword
    arguments (to pass to :meth:`~kingfisher_scrapy.base_spiders.BaseSpider.build_request`).

    If the results are in ascending chronological order, set ``chronological_order = 'asc'``.

    The ``parse_list()`` method parses responses as JSON data. To change the parser of these responses - for example,
    to check for an error response or extract the page count from an HTML page - override the ``parse_list_loader()``
    method. If this method returns a ``FileError``, then ``parse_list()`` yields it and returns.

    Otherwise, results are yielded from all responses by :meth:`~kingfisher_scrapy.SimpleSpider.parse`. To
    change this method, set a ``parse_list_callback`` class attribute to a method's name as a string.

    The names of the query string parameters 'page', 'limit' and 'offset' are customizable. Define the ``param_page``,
    ``param_limit`` and ``param_offset`` class attributes to set the custom names.

    If a different URL is used for the initial request than for later requests, set the ``base_url`` class attribute
    to the base URL of later requests. In this case, results aren't yielded from the response passed to ``parse_list``.
    """

    use_page = False
    start_page = 1
    chronological_order = 'desc'
    parse_list_callback = 'parse'
    param_page = 'page'
    param_limit = 'limit'
    param_offset = 'offset'
    base_url = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parse_list_callback = getattr(self, self.parse_list_callback)

        has_page_count_pointer = hasattr(self, 'page_count_pointer')
        has_result_count_pointer = hasattr(self, 'result_count_pointer')
        has_range_generator = hasattr(self, 'range_generator')

        if not (has_page_count_pointer ^ has_result_count_pointer ^ has_range_generator):
            raise IncoherentConfigurationError(
                'Exactly one of page_count_pointer, result_count_pointer or range_generator must be set.')
        if self.use_page and not has_result_count_pointer:
            raise IncoherentConfigurationError(
                'use_page = True has no effect unless result_count_pointer is set.')

        if has_page_count_pointer:
            self.range_generator = self.page_count_range_generator
            if not hasattr(self, 'url_builder'):
                self.url_builder = self.pages_url_builder
            if not hasattr(self, 'formatter'):
                self.formatter = parameters(self.param_page)
        elif has_result_count_pointer:
            if self.use_page:
                self.range_generator = self.result_count_range_generator
                if not hasattr(self, 'url_builder'):
                    self.url_builder = self.pages_url_builder
                if not hasattr(self, 'formatter'):
                    self.formatter = parameters(self.param_page)
            else:
                self.range_generator = self.limit_offset_range_generator
                if not hasattr(self, 'url_builder'):
                    self.url_builder = self.limit_offset_url_builder
                if not hasattr(self, 'formatter'):
                    self.formatter = parameters(self.param_offset)

    @handle_http_error
    def parse_list(self, response):
        data = self.parse_list_loader(response)
        if isinstance(data, FileError):
            yield data
            return

        if not self.base_url:
            yield from self.parse_list_callback(response)

        for priority, value in enumerate(self.range_generator(data, response)):
            # Requests with a higher priority value will execute earlier and we want the newest pages first.
            # https://doc.scrapy.org/en/latest/topics/request-response.html#scrapy.http.Request
            if self.chronological_order == 'desc':
                priority *= -1
            return_value = self.url_builder(value, data, response)
            if isinstance(return_value, tuple):
                url, kwargs = return_value
            else:
                url, kwargs = return_value, {}
            yield self.build_request(
                url,
                formatter=self.formatter,
                priority=priority,
                callback=self.parse_list_callback,
                **kwargs,
            )

    def parse_list_loader(self, response):
        return response.json()

    def page_count_range_generator(self, data, response):
        pages = resolve_pointer(data, self.page_count_pointer)
        start = 0 if self.base_url else 1
        return range(self.start_page + start, self.start_page + pages)

    def pages_url_builder(self, value, data, response):
        return self._build_url(response, {
            self.param_page: value,
        })

    def limit_offset_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.result_count_pointer)
        start = 0 if self.base_url else limit
        return range(start, count, limit)

    def limit_offset_url_builder(self, value, data, response):
        limit = self._resolve_limit(data)
        return self._build_url(response, {
            self.param_limit: limit,
            self.param_offset: value,
        })

    def result_count_range_generator(self, data, response):
        limit = self._resolve_limit(data)
        count = resolve_pointer(data, self.result_count_pointer)
        start = 0 if self.base_url else 1
        return range(self.start_page + start, self.start_page + ceil(count / limit))

    def _resolve_limit(self, data):
        if isinstance(self.limit, str) and self.limit.startswith('/'):
            return resolve_pointer(data, self.limit)
        return int(self.limit)

    def _build_url(self, response, params):
        return util.replace_parameters(self.base_url or response.request.url, **params.copy())
