from kingfisher_scrapy.spiders.panama_dgcp_base import PanamaDGCPBase


class PanamaDGCPRecords(PanamaDGCPBase):
    """
    Domain
      Panama Dirección General de Contrataciones Públicas (DGCP)
    Swagger API documentation
      https://ocds.panamacompraencifras.gob.pa/swagger/index.html
    """
    name = 'panama_dgcp_records'

    # SimpleSpider
    data_type = 'record_package'

    # PanamaDGCPBase
    url_path = 'Record'
