from kingfisher_scrapy.spiders.honduras_portal_base import HondurasPortalBase


class HondurasPortalRecords(HondurasPortalBase):
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
    name = 'honduras_portal_records'

    # BaseSpider
    root_path = 'recordPackage'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases

    # SimpleSpider
    data_type = 'record_package'

    url = 'http://www.contratacionesabiertas.gob.hn/api/v1/record/?format=json'
