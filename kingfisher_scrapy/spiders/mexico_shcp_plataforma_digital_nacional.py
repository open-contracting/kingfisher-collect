from kingfisher_scrapy.spiders.mexico_plataforma_digital_nacional_base import MexicoPlataformaDigitalNacionalBase


class MexicoSHCPPlataformaDigitalNacional(MexicoPlataformaDigitalNacionalBase):
    """
    Domain
      Secretaría de Hacienda y Crédito Público (SHCP) (Mexico) - Plataforma Digital Nacional
    Bulk download documentation
      https://plataformadigitalnacional.org/contrataciones
    """

    name = 'mexico_shcp_plataforma_digital_nacional'

    # MexicoPlataformaDigitalNacionalBase
    publisher_id = 'SHCP'
