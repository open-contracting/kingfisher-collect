from kingfisher_scrapy.spiders.mexico_plataforma_digital_nacional_base import MexicoPlataformaDigitalNacionalBase


class MexicoVeracruzStateSESEAPlataformaDigitalNacional(MexicoPlataformaDigitalNacionalBase):
    """
    Domain
      Secretaría Ejecutiva del Sistema Estatal Anticorrupción de Veracruz de Ignacio de la Llave (SESEA) (Mexico) -
      Plataforma Digital Nacional
    Bulk download documentation
      https://plataformadigitalnacional.org/contrataciones
    """
    name = 'mexico_veracruz_state_sesea_plataforma_digital_nacional'

    # MexicoPlataformaDigitalNacionalBase
    publisher_id = 'SESEA_VER'
