from kingfisher_scrapy.spiders.panama_dgcp_base import PanamaDGCPBase


class PanamaDGCPReleases(PanamaDGCPBase):
    """
    Domain
      Panama Dirección General de Contrataciones Públicas (DGCP)
    Swagger API documentation
      https://ocds.panamacompraencifras.gob.pa/swagger/index.html
    """

    name = 'panama_dgcp_releases'

    # SimpleSpider
    data_type = 'release_package'

    # PanamaDGCPBase
    url_path = 'Release'
