from kingfisher_scrapy.spiders.mexico_plataforma_digital_nacional_base import MexicoPlataformaDigitalNacionalBase


class MexicoMichoacanSESEAPlataformaDigitalNacional(MexicoPlataformaDigitalNacionalBase):
    """
    Domain
      Secretaría Ejecutiva del Sistema Estatal Anticorrupción del Estado de Michoacán (SESEA) (Mexico) -
      Plataforma Digital Nacional
    Bulk download documentation
      https://plataformadigitalnacional.org/contrataciones
    """
    name = 'mexico_michoacan_sesea_plataforma_digital_nacional'

    # MexicoPlataformaDigitalNacionalBase
    publisher_id = 'SESEA_MCH'
