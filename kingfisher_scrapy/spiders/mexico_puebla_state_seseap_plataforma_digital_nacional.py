from kingfisher_scrapy.spiders.mexico_plataforma_digital_nacional_base import MexicoPlataformaDigitalNacionalBase


class MexicoPueblaStateSESEAPPlataformaDigitalNacional(MexicoPlataformaDigitalNacionalBase):
    """
    Domain
      Secretaría Ejecutiva del Sistema Estatal Anticorrupción del Estado de Puebla (SESEAP) (Mexico) -
      Plataforma Digital Nacional
    Bulk download documentation
      https://plataformadigitalnacional.org/contrataciones
    """
    name = 'mexico_puebla_state_seseap_plataforma_digital_nacional'

    # MexicoPlataformaDigitalNacionalBase
    publisher_id = 'SESAE_PUE'
