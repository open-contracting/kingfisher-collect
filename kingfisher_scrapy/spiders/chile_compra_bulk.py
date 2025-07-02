import json

from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.items import File
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT, components

# curl -I https://ocds.blob.core.windows.net/ocds/202205.zip


class ChileCompraBulk(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      ChileCompra
    Caveats
      This dataset was last updated by the publisher in 2022.
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2009-01'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    Bulk download documentation
      https://desarrolladores.mercadopublico.cl/OCDS/DescargaMasiva
    """

    name = "chile_compra_bulk"
    download_timeout = MAX_DOWNLOAD_TIMEOUT
    custom_settings = {
        "DOWNLOAD_FAIL_ON_DATALOSS": False,
    }

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # chile_compra_api_records

    # SimpleSpider
    data_type = "record_package"

    # BaseSpider
    date_format = "year-month"
    default_from_date = "2009-01"

    # PeriodicSpider
    pattern = "https://ocds.blob.core.windows.net/ocds/{0:%Y}{0:%m}.zip"
    formatter = staticmethod(components(-1))  # filename containing year-month

    def build_file(self, *, file_name=None, url=None, data_type=None, data=None):
        """
        Some files contain invalid record packages, like:

        {
          "status": 500,
          "detail": "error"
        }
        """
        parsed = json.loads(data)

        if parsed.get("status") != 200:
            self.logger.error(
                "status=%d message=%r request=<GET %s> file_name=%s",
                parsed["status"],
                parsed["detail"],
                url,
                file_name,
            )

        return File(file_name=file_name, url=url, data_type=None, data=data)
