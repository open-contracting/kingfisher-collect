import datetime

from kingfisher_scrapy.base_spiders import BigFileSpider, CKANSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, MAX_DOWNLOAD_TIMEOUT, components


class ItalyANAC(CKANSpider, BigFileSpider):
    """
    Domain
      Autorità Nazionale Anticorruzione (ANAC)
    Caveats
      If the OCID is missing, the spider derives the ``ocid`` field from the ``id`` field.
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2018-01'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    API documentation
      https://dati.anticorruzione.it/opendata/about
    Bulk download documentation
      https://dati.anticorruzione.it/opendata/organization/anticorruzione
    """

    name = "italy_anac"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": MAX_DOWNLOAD_TIMEOUT * 2,  # 1h
        "USER_AGENT": BROWSER_USER_AGENT,  # Otherwise, API returns "Request Rejected" HTML
    }

    # BaseSpider
    date_format = "year-month"
    default_from_date = "2018-01"

    # SimpleSpider
    data_type = "release_package"

    # CKANSpider
    ckan_api_url = "https://dati.anticorruzione.it/opendata"
    ckan_search_query = "ocds"
    # e.g. https://dati.anticorruzione.it/opendata/download/dataset/ocds/filesystem/bulk/2022/01.json
    formatter = components(-2)

    # CKANSpider
    def get_resource_date(self, resource):
        year, month = self.formatter(resource["url"]).split("-")
        return datetime.datetime(int(year), int(month), 1, tzinfo=datetime.timezone.utc)

    # ResizePackageMiddleware
    def ocid_fallback(self, release):
        # Extract the ocid from the release id as a fallback, like ocds-hu01ve-7608611 from ocds-hu01ve-7608611-01.
        return "-".join(release["id"].split("-")[:3])
