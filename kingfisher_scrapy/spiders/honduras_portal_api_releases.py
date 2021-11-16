from kingfisher_scrapy.spiders.honduras_portal_api_base import HondurasPortalAPIBase


class HondurasPortalAPIReleases(HondurasPortalAPIBase):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Secretaria de Finanzas de Honduras (SEFIN)
    Spider arguments
      publisher
        Filter by publisher:

        oncae
          Oficina Normativa de Contratación y Adquisiciones del Estado
        sefin
          Secretaria de Finanzas de Honduras
    API documentation
      http://www.contratacionesabiertas.gob.hn/manual_api/
    Swagger API documentation
      http://www.contratacionesabiertas.gob.hn/servicio/
    """
    name = 'honduras_portal_api_releases'

    # BaseSpider
    root_path = 'releasePackage'

    # SimpleSpider
    data_type = 'release_package'

    start_url = 'http://www.contratacionesabiertas.gob.hn/api/v1/release/?format=json'
