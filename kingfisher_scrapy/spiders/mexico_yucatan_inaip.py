from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoYucatan(MexicoINAIBase):
    """
    Domain
      Instituto Estatal de Transparencia, Acceso a la Información Pública y Protección de Datos Personales
      (INAIP) - Yucatán
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2020'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2020'.
    API documentation
      https://contratacionesabiertas.inaipyucatan.org.mx/contratacionesabiertas/datosabiertos#
    """
    name = 'mexico_yucatan_inaip'

    # BaseSpider
    default_from_date = '2020'
    default_until_date = '2020'

    # PeriodicSpider
    pattern = 'https://captura.contratacionesabiertas.inaipyucatan.org.mx/edca/contractingprocess/{}'
