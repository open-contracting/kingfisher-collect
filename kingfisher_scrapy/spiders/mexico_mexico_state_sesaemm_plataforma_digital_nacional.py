from kingfisher_scrapy.spiders.mexico_plataforma_digital_nacional_base import MexicoPlataformaDigitalNacionalBase


class MexicoMexicoStateSESAEMMPlataformaDigitalNacional(MexicoPlataformaDigitalNacionalBase):
    """
    Domain
      Secretaría Ejecutiva del Sistema Estatal Anticorrupción del Estado de México y Municipios (SESAEMM) (Mexico) -
      Plataforma Digital Nacional
    Bulk download documentation
      https://plataformadigitalnacional.org/contrataciones
    """
    name = 'mexico_mexico_state_sesaemm_plataforma_digital_nacional'

    # MexicoPlataformaDigitalNacionalBase
    publisher_id = 'SESAEMM_EDOMEX'
