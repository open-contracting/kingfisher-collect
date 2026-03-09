from kingfisher_scrapy.spiders.peru_oece_api_base import PeruOECEAPIBase


class PeruOECEAPIReleases(PeruOECEAPIBase):
    """
    Domain
      Organismo Especializado para las Contrataciones Públicas Eficientes (OECE)
    API documentation
      https://contratacionesabiertas.oece.gob.pe/api
    """

    name = "peru_oece_api_releases"

    # SimpleSpider
    data_type = "release_package"

    # PeruOECEAPIBase
    endpoint = "releasesAfter"
