from kingfisher_scrapy.spiders.peru_osce_api_base import PeruOSCEAPIBase


class PeruOSCEAPIReleases(PeruOSCEAPIBase):
    """
    Domain
      Organismo Supervisor de las Contrataciones del Estado (OSCE)
    API documentation
      https://contratacionesabiertas.osce.gob.pe/api
    """

    name = "peru_osce_api_releases"

    # SimpleSpider
    data_type = "release_package"

    # PeruOSCEBase
    endpoint = "releasesAfter"
