from kingfisher_scrapy.spiders.mexico_nuevo_leon_infra_abierta_base import MexicoNuevoLeonBase


class MexicoNuevoLeonInfraAbiertaRecords(MexicoNuevoLeonBase):
    """
    Domain
      Secretaría de Movilidad y Planeación Urbana de Nuevo León
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2013'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://smpu.nl.gob.mx/transparencia/publicaciones
    """

    name = 'mexico_nuevo_leon_infra_abierta_records'

    # BaseSpider
    root_path = 'item'

    # SimpleSpider
    data_type = 'record_package'

    def build_file_item(self, number, data, item):
        # The 'anio' query parameter looks like anio-[{"value":"2024"}].json
        item.file_name = item.file_name.replace('[{"value":"', '').replace('"}]', '')
        return super().build_file_item(number, data, item)
