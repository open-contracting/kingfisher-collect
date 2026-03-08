from kingfisher_scrapy.base_spiders import CKANSpider, SimpleSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, components


class MexicoNuevoLeon(CKANSpider, SimpleSpider):
    """
    Domain
      Nuevo León - Dirección General de Adquisiciones y Servicios - Secretaría de Administración
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2024-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    Bulk download documentation
      https://catalogodatos.nl.gob.mx/dataset/contrataciones-abiertas-direccion-general-de-adquisiciones-y-servicios
    """

    name = "mexico_nuevo_leon"
    custom_settings = {
        "USER_AGENT": BROWSER_USER_AGENT,  # to avoid HTTP 403
    }

    # BaseSpider
    default_from_date = "2024-01-01"

    # SimpleSpider
    data_type = "release_package"

    # CKANSpider
    ckan_api_url = "https://catalogodatos.nl.gob.mx"
    ckan_package_id = "contrataciones-abiertas-direccion-general-de-adquisiciones-y-servicios"
    # Format can be "JSON" or "URL".
    ckan_resource_format = None
    # e.g. https://api-ocds.nl.gob.mx/api/releases/673d316c7e60f2c8230bcf15
    formatter = components(-1)
