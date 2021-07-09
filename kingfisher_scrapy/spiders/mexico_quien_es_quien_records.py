from kingfisher_scrapy.spiders.mexico_quien_es_quien_base import MexicoQuienEsQuienBase


class MexicoQuienEsQuienRecords(MexicoQuienEsQuienBase):
    """
    Domain
      QuiénEsQuién.Wiki
    API documentation
      https://qqwapi-elastic.readthedocs.io/es/latest/
    Swagger API documentation
      https://api.quienesquien.wiki/v3/docs/
    """
    name = 'mexico_quien_es_quien_records'

    # SimpleSpider
    data_type = 'record_package'

    # IndexSpider
    base_url = 'https://api.quienesquien.wiki/v3/record'
