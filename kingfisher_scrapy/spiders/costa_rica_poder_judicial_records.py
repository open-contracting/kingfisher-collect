from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class CostaRicaPoderJudicialRecords(PeriodicSpider):
    """
    Domain
      Poder Judicial de Costa Rica
    Spider arguments
      from_date
        Download only data from this month onward (YYYY format). Defaults to '2016'.
      until_date
        Download only data until this month (YYYY format). Defaults to the current year.
    Bulk download documentation
      http://datosabiertospj.eastus.cloudapp.azure.com/dataset/estandar-de-datos-de-contrataciones-abiertas-ocds
    """

    name = 'costa_rica_poder_judicial_records'
    data_type = 'record_package'

    # PeriodicSpider variables
    date_format = 'year'
    default_from_date = '2016'
    pattern = 'https://pjcrdatosabiertos.blob.core.windows.net/datosabiertos/OpenContracting/{}.json'

    def get_formatter(self):
        return components(-1)
