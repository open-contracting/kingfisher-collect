from kingfisher_scrapy.spiders.panama_dgcp_base import PanamaDGCPBase


class PanamaDGCPRecords(PanamaDGCPBase):
    """
    Domain
      Dirección General de Contrataciones Públicas (DGCP)
    Swagger API documentation
      https://ocds.panamacompraencifras.gob.pa/swagger/index.html
    """

    name = 'panama_dgcp_records'

    # BaseSpider
    validate_json = True  # https://github.com/open-contracting/kingfisher-collect/issues/1036

    # SimpleSpider
    data_type = 'record_package'

    # PanamaDGCPBase
    url_path = 'Record'
