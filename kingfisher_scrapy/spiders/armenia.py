import math
from urllib.parse import parse_qs, urlsplit

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters, replace_parameter


class Armenia(LinksSpider):
    """
    If the API returns an error in ``next_page``, a binary search is performed to retrieve the success download cycle.
    The search range extends for a maximum of 10 consecutive days from the last day of the successful download.
    Spider arguments
      sample
        Download only the first release package in the dataset.
    """
    name = 'armenia'
    data_type = 'release_package'
    next_pointer = '/next_page/uri'
    next_page_formatter = staticmethod(parameters('offset'))
    last_page_success = None
    next_page_error = None
    days = 1

    custom_settings = {
        'RETRY_TIMES': 1,
        'CONCURRENT_REQUESTS': 1,
    }

    def start_requests(self):
        url = 'https://armeps.am/ocds/release'
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'})

    def parse_next_link(self, response):
        # check if there is a search in process
        binary_search = True if 'minimum' in response.request.meta else False

        if self.is_http_success(response):
            # save this page for the lowest offset that works or the page with next_page error
            self.last_page_success = response.request.url
            if binary_search:
                # continue the search with http success
                return self.binary_search(response, succeed=True)

            # next_page works
            return self.build_request(response.request.url, dont_filter=True, formatter=parameters('offset'))

        if binary_search:
            # continue the search with http error
            return self.binary_search(response, succeed=False)

        # save the page with next_page error
        self.next_page_error = self.last_page_success
        # start a binary search
        return self.binary_search(response, start='start')

    def binary_search(self, response, succeed=None, start=None):
        microseconds_per_day = 86400000
        if start:
            if start == 'start':
                # start with last number that worked as the minimum
                minimum = self.get_offset(self.next_page_error)
            else:
                # set the minimum to the maximum
                minimum = self.get_offset(response.request.url)
            # start with one day in the future of the current minimum as the maximum
            maximum = minimum + (microseconds_per_day * self.days)
        else:
            if succeed:
                # if it succeeds, set the midpoint to the maximum
                maximum = self.get_offset(response.request.url)
                # keep the minimum
                minimum = response.request.meta['minimum']
            else:
                # if it errors, assume that all intervening offsets would also error
                minimum = self.get_offset(response.request.url)
                # keep the maximum
                maximum = response.request.meta['maximum']

                # check if start trying with the maximum
                if maximum == minimum:
                    if self.days == 10:
                        # binary search finished, reached 10 consecutive days without response
                        self.logger.info(f'No next_page found for page: {self.next_page_error}')
                        return
                    # advance the maximum in one day and restart the search
                    self.days = self.days + 1
                    return self.binary_search(response, succeed, start='restart')

        if maximum - minimum != 1:
            # midpoint did not stop moving, continue binary search
            if start:
                offset = maximum  # start trying with the maximum
            else:
                offset = math.floor((maximum + minimum) / 2)  # calculate midpoint
            url = replace_parameter(response.request.url, 'offset', offset)
            meta = {'minimum': minimum, 'maximum': maximum}
            self.logger.info(f'Searching, minimum: {minimum}, midpoint: {offset}, maximum: {maximum}')
            return self.build_request(url, dont_filter=True, meta=meta, formatter=parameters('offset'),
                                      callback=self.parse_next_link)

        # midpoint stop moving, binary search finished
        self.logger.info(f'New next_page found for page: {self.next_page_error}, next_page: {self.last_page_success}')
        self.days = 1  # reset days for future searches
        # request the lowest offset that works
        return self.build_request(self.last_page_success, dont_filter=True, formatter=parameters('offset'))

    @staticmethod
    def get_offset(url):
        query = parse_qs(urlsplit(url).query)
        return int(query['offset'][0])
