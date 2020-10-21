from kingfisher_scrapy.spiders.honduras_portal_base import HondurasPortalBase


class HondurasPortalRecords(HondurasPortalBase):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Secretaria de Finanzas de Honduras (SEFIN)
    API documentation
      http://www.contratacionesabiertas.gob.hn/manual_api/
    Swagger API documentation
      http://www.contratacionesabiertas.gob.hn/servicio/
    Spider arguments
      publisher
        Filter by publisher:

        oncae
          Oficina Normativa de Contratación y Adquisiciones del Estado
        sefin
          Secretaria de Finanzas de Honduras
    """
    name = 'honduras_portal_records'
    data_type = 'record_package'
    data_pointer = '/recordPackage'
    skip_pluck = 'Already covered (see code for details)'  # honduras_portal_releases
    url = 'http://www.contratacionesabiertas.gob.hn/api/v1/record/?format=json'
