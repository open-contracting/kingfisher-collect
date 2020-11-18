from kingfisher_scrapy.spiders.honduras_portal_base import HondurasPortalBase


class HondurasPortalReleases(HondurasPortalBase):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Secretaria de Finanzas de Honduras (SEFIN)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DDTHH:mm:ss format).
        If ``until_date`` is provided, defaults to '2000-01-01T00:00:00'.
      until_date
        Download only data until this date (YYYY-MM-DDTHH:mm:ss format).
        If ``from_date`` is provided, defaults to today.
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
    name = 'honduras_portal_releases'
    data_type = 'release_package'
    data_pointer = '/releasePackage'
    url = 'http://www.contratacionesabiertas.gob.hn/api/v1/release/?format=json'
