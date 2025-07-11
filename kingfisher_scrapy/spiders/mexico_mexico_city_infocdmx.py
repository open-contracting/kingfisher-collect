from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase
from kingfisher_scrapy.util import BROWSER_USER_AGENT


class MexicoMexicoCityINFOCDMX(MexicoINAIBase):
    """
    Domain
      Instituto de Transparencia, Acceso a la Información Pública, Protección de Datos Personales y Rendición de
      Cuentas de la Ciudad de México (INFOCDMX)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2019'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      https://dashboard.infocdmx.org.mx/contratacionesabiertas/datosabiertos
    """

    name = "mexico_mexico_city_infocdmx"
    user_agent = BROWSER_USER_AGENT  # to avoid HTTP 500

    # BaseSpider
    default_from_date = "2019"

    # MexicoINAIBase
    base_url = "https://contratacionesabiertas.infocdmx.org.mx:3000"
