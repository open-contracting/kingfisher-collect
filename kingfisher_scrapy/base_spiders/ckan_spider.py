import datetime

import scrapy


class CKANSpider:
    """
    Collect data from a CKAN API.

    #. Inherit from ``CKANSpider`` and another base spider class that defines the ``parse()`` method
       (like ``SimpleSpider``, ``CompressedFileSpider``, ``BigFileSpider``)
    #. Set a ``ckan_api_url`` class attribute to the base URL, before ``/api/3/action/``
    #. Set one of:

       -  ``ckan_package_id``, if files are under one resource
       -  ``ckan_search_query``, if files are under many resources

    #. Set a ``formatter`` class attribute to set the file name like in
       :meth:`~kingfisher_scrapy.base_spiders.BaseSpider.build_request`
    #. Optionally, set a ``ckan_resource_format`` class attribute to filter by format (default "JSON")
    #. Optionally, override ``get_resource_date()`` to use a different date for date filtering (default ``created``)

    .. code-block:: python

        from kingfisher_scrapy.base_spiders import CKANSpider, SimpleSpider

        class MySpider(CKANSpider, SimpleSpider):
            name = 'my_spider'

            # SimpleSpider
            data_type = 'release_package'

            # CKANSpider
            ckan_api_url = 'https://example.com'
            ckan_package_id = 'my-dataset-id'
    """

    ckan_api_url = ""
    ckan_search_query = ""
    ckan_package_id = ""
    ckan_resource_format = "JSON"

    async def start(self):
        # https://docs.ckan.org/en/latest/api/#get-able-api-functions
        if self.ckan_search_query:
            url = f"{self.ckan_api_url}/api/3/action/package_search?q={self.ckan_search_query}&rows=1000"
        else:
            url = f"{self.ckan_api_url}/api/3/action/package_show?id={self.ckan_package_id}"
        yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        for resource in self._resources(response.json()):
            if self.ckan_resource_format and resource["format"].upper() != self.ckan_resource_format:
                continue
            date = self.get_resource_date(resource)
            if self.from_date and self.until_date and not (self.from_date <= date <= self.until_date):
                continue

            yield self.build_request(resource["url"], formatter=self.formatter)

    def get_resource_date(self, resource):
        """
        Return the resource's ``created`` datetime, for date filtering.

        .. attention::

           The resource's ``created`` field might not match the data's temporal coverage.

        Override this method to, for example, extract the date from the URL.
        """
        return datetime.datetime.strptime(resource["created"], "%Y-%m-%dT%H:%M:%S.%f").replace(
            tzinfo=datetime.timezone.utc
        )

    def _resources(self, data):
        if "results" in data["result"]:  # package_search
            for result in data["result"]["results"]:
                yield from result["resources"]
        else:  # package_show
            yield from data["result"]["resources"]
