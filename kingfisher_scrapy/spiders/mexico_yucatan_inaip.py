from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoYucatanINAIP(MexicoINAIBase):
    """
    Domain
      Instituto Estatal de Transparencia, Acceso a la Información Pública y Protección de Datos Personales
      (INAIP) - Yucatán
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2020'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      https://contratacionesabiertas.inaipyucatan.org.mx/contratacionesabiertas/datosabiertos#
    """

    name = "mexico_yucatan_inaip"

    # BaseSpider
    default_from_date = "2020"

    # MexicoINAIBase
    base_url = "https://captura.contratacionesabiertas.inaipyucatan.org.mx"
