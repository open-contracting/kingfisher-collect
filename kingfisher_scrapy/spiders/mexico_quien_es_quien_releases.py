from kingfisher_scrapy.base_spiders import IndexSpider, PeriodicSpider
from kingfisher_scrapy.util import parameters


class MexicoQuienEsQuienReleases(IndexSpider, PeriodicSpider):
    """
    Domain
      QuiénEsQuién.Wiki
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '1999-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to '2021-12-31'.
    API documentation
      https://qqwapi-elastic.readthedocs.io/es/latest/
    Swagger API documentation
      https://api.quienesquien.wiki/v3/docs/
    """
    name = 'mexico_quien_es_quien_releases'

    # BaseSpider
    default_from_date = '1999-01-01'
    default_until_date = '2021-12-31'
    date_format = 'date'
    root_path = 'data.item'

    # SimpleSpider
    data_type = 'release'

    # IndexSpider
    result_count_pointer = '/count'
    limit = 1000

    # PeriodicSpider
    formatter = staticmethod(parameters('start_date_min', 'start_date_max', 'offset'))
    pattern = (
        'https://api.quienesquien.wiki/v3/contracts?start_date_min={0:%Y-%m-%d}&start_date_max={1:%Y-%m-%d}'
        f'&offset=0&limit={limit}'
    )
    start_requests_callback = 'parse_list'
