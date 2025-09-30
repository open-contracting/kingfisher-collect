from kingfisher_scrapy.spiders.peru_oece_api_base import PeruOECEAPIBase


class PeruOECEAPIRecords(PeruOECEAPIBase):
    """
    Domain
      Organismo Especializado para las Contrataciones Públicas Eficientes (OECE)
    API documentation
      https://contratacionesabiertas.oece.gob.pe/api
    """

    name = "peru_oece_api_records"

    # SimpleSpider
    data_type = "record_package"

    # PeruOSCEBase
    endpoint = "recordsAfter"
