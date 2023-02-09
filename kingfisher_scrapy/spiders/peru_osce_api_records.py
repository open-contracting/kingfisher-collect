from kingfisher_scrapy.spiders.peru_osce_api_base import PeruOSCEAPIBase


class PeruOSCEAPIRecords(PeruOSCEAPIBase):
    """
    Domain
      Organismo Supervisor de las Contrataciones del Estado (OSCE)
    API documentation
      https://contratacionesabiertasdesa.osce.gob.pe/api
    """
    name = 'peru_osce_api_records'

    # SimpleSpider
    data_type = 'record_package'

    # PeruOSCEBase
    endpoint = 'records'
