from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components


class Bulgaria(PeriodicSpider):
    """
    Domain
      Public Procurement Agency (PPA)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2026-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Bulk download documentation
      https://app.eop.bg/today/reporting/open-data
    """

    name = "bulgaria"

    # BaseSpider
    date_format = "date"
    default_from_date = "2026-01-01"

    # SimpleSpider
    data_type = "release_package"

    # PeriodicSpider
    pattern = (
        "https://storage.eop.bg/open-data-{0:%Y-%m-%d}/"
        "Автоматично генерирани данни за обявления, публикувани в ЦАИС ЕОП на "
        "{0:%d.%m.%Y} г., съгласно стандарт OCDS.json"  # noqa: RUF001
    )
    formatter = staticmethod(components(-2, -1))
