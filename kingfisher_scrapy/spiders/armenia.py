import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import get_parameter_value, parameters, replace_parameter

MILLISECONDS_PER_DAY = 86400000
EXPONENT_LIMIT = 10  # 1024 days
THRESHOLD = 2700000  # 45 minutes / 5 iterations within 1 day


class Armenia(LinksSpider):
    """
    The API paginates results using an ``offset`` query string parameter, which is a timestamp. If a timestamp causes
    an error, the spider will try to find the nearest timestamp within the following 1024 days that succeeds.

    Spider arguments
      sample
        Download only the first release package in the dataset.
    """
    name = 'armenia'
    next_pointer = '/next_page/uri'
    next_page_formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        url = 'https://armeps.am/ocds/release'
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'})

    def parse(self, response):
        # If the request was successful, parse the response as usual.
        if self.is_http_success(response):
            yield self.build_file_from_response(response, data_type='release_package')

            # Use `dont_filter` in case the search for a successful timestamp used the same offset. Use `dont_retry`
            # since errors are expected.
            if not self.sample:
                yield self.next_link(response, dont_filter=True, meta={'dont_retry': True})
        # Otherwise, parse the response as usual, then (1) pick a date range and (2) do a binary search within it.
        # This approach assumes that, if two offsets error, then intervening offsets error, too.
        else:
            yield self.build_file_error_from_response(response)

            # If the error occurs on the first request, we have no starting offset.
            if get_parameter_value(response.request.url, 'offset'):
                yield from self.parse_date_range(response)

    # Exponential search (https://en.wikipedia.org/wiki/Exponential_search). We can do an elaborate alternative
    # (https://www.slac.stanford.edu/cgi-bin/getdoc/slac-pub-1679.pdf), but we keep it simpler for now.
    def parse_date_range(self, response):
        offset = get_parameter_value(response.request.url, 'offset')

        # Scrapy uses `datetime.datetime.utcnow()`, so we don't need to worry about time zones.
        start_time = int(self.crawler.stats.get_value('start_time').timestamp() * 1000)
        # We use the first offset to calculate the new offset, and in log lessages.
        first_offset = response.request.meta.get('first', offset)
        # The exponent for the exponential search.
        exponent = response.request.meta.get('exponent', -1) + 1

        # If this offset succeeded, do a binary search from the previous offset to this offset.
        if self.is_http_success(response):
            yield from self.parse_binary_search(response, response.request.meta['prev'], offset)
        # If this offset failed and reached a limit, stop.
        elif offset >= start_time or exponent > EXPONENT_LIMIT:
            self.logger.info(f'No offset found after {first_offset:,} within {2 ** EXPONENT_LIMIT} days.')
            yield self.build_file_error_from_response(response)
        # Otherwise, continue.
        else:
            new_offset = min(first_offset + MILLISECONDS_PER_DAY * 2 ** exponent, start_time)
            url = replace_parameter(response.request.url, 'offset', new_offset)
            yield self._build_request(url, self.parse_date_range, {'prev': offset, 'exponent': exponent,
                                                                   'first': first_offset})

    # We use one of the alternative binary search methods (https://en.wikipedia.org/wiki/Binary_search_algorithm),
    # because we only know if an offset succeeds, not whether an offset is greater than the target value.
    def parse_binary_search(self, response, minimum=None, maximum=None):
        offset = get_parameter_value(response.request.url, 'offset')

        first_offset = response.request.meta['first']

        if minimum and maximum:
            self.logger.info(f'Starting binary search for {first_offset:,} within [{minimum:,}, {maximum:,}]')
        elif self.is_http_success(response):
            minimum = response.request.meta['minimum']
            maximum = offset
        else:
            minimum = offset + 1
            maximum = response.request.meta['maximum']

        # If the search succeeded, parse the response as usual. We use a threshold, because getting the exact
        # millisecond requires 27 requests.
        if minimum + THRESHOLD >= maximum:
            self.logger.info(f'New offset found after {first_offset:,} at {maximum:,}!')
            if offset == maximum:
                # If the last request used the offset, we can reuse its response.
                yield from self.parse(response)
            else:
                url = replace_parameter(response.request.url, 'offset', maximum)
                yield self._build_request(url, self.parse, {})
        else:
            url = replace_parameter(response.request.url, 'offset', (minimum + maximum) // 2)
            yield self._build_request(url, self.parse_binary_search, {'minimum': minimum, 'maximum': maximum,
                                                                      'first': first_offset})

    def _build_request(self, url, callback, meta):
        meta['dont_retry'] = True
        # We need to set `formatter` in case we want to re-use the response to build a file or file error.
        return self.build_request(url, formatter=parameters('offset'), dont_filter=True, meta=meta, callback=callback)
