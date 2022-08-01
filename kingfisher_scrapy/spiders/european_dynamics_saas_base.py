import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class EuropeanDynamicsSaasBase(SimpleSpider):
    """
    This class makes it easy to collect data from an European Dynamics SaaS Electronic Procurement:

    #. Inherit from ``EuropeanDynamicsSaasBase``
    #. Set a ``base_url`` class attribute with the portal's domain

    .. code-block:: python

        from kingfisher_scrapy.spiders.european_dynamics_saas_base import EuropeanDynamicsSaasBase

        class MySpider(EuropeanDynamicsSaasBase):
            name = 'my_spider'

            # EuropeanDynamicsSaasBase
            base_url = 'http://base-url'
    """

    # SimpleSpider
    data_type = 'release_package'

    # base_url must be provided by subclasses.

    def start_requests(self):
        url = f'{self.base_url}Home/Procurements/'
        yield scrapy.Request(url, meta={'file_name': 'all.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        pattern = '//table[@id="datable_3"]/tbody/tr/td[2]/span/a/@href'
        for item in response.xpath(pattern).re("[0-9]+"):
            yield self.build_request(f'{self.base_url}openapi/packagesapi/{item}', formatter=components(-1))
