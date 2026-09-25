from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoJaliscoSESAJ(MexicoINAIBase):
    """
    Domain
      Secretaría Ejecutiva del Sistema Anticorrupción del Estado de Jalisco (SESAJ)
    Caveats
      Some years listed by the API return HTTP 404 (e.g. 2025).
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2025'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      https://contratacionesabiertas.sesaj.org/contratacionesabiertas/datosabiertos#
    """

    name = "mexico_jalisco_sesaj"

    # BaseSpider
    default_from_date = "2025"

    # MexicoINAIBase
    base_url = "https://captura-contrataciones.sesaj.org"
