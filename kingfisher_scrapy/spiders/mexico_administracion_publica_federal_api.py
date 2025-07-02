import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider


class MexicoAdministracionPublicaFederalAPI(IndexSpider):
    """
    Domain
      Administración Pública Federal (APF): Secretaria de la Función Pública (SFP) - Secretaría de Hacienda y Crédito
      Público (SHCP)
    Caveats
      This dataset was last updated by the publisher in 2018.
    API documentation
      https://www.datos.gob.mx/busca/dataset/api-de-contrataciones-abiertas-de-la-apf
    """

    name = "mexico_administracion_publica_federal_api"

    # BaseSpider
    root_path = "results.item"
    skip_pluck = "Already covered (see code for details)"  # mexico_administracion_publica_federal_bulk

    # SimpleSpider
    data_type = "record_package"

    # IndexSpider
    result_count_pointer = "/pagination/total"
    limit = "/pagination/pageSize"
    use_page = True

    def start_requests(self):
        # The pageSize query string parameter can be increased, but large values (like 10000) cause service failure.
        url = "https://api.datos.gob.mx/v2/contratacionesabiertas"
        # The pages are in reverse chronological order.
        yield scrapy.Request(url, meta={"file_name": "page-1.json"}, callback=self.parse_list)
