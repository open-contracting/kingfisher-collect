from kingfisher_scrapy.spiders.mexico_nuevo_leon_infra_abierta_base import MexicoNuevoLeonBase
from kingfisher_scrapy.util import components, handle_http_error


class MexicoNuevoLeonInfraAbiertaReleases(MexicoNuevoLeonBase):
    """
    Domain
      Secretaría de Movilidad y Planeación Urbana de Nuevo León
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2013'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://smpu.nl.gob.mx/transparencia/acerca-del-proyecto
    """

    name = "mexico_nuevo_leon_infra_abierta_releases"

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # mexico_nuevo_leon_records

    # SimpleSpider
    data_type = "release_package"

    # PeriodicSpider
    start_requests_callback = "parse_list"

    @handle_http_error
    def parse_list(self, response):
        for record_package in response.json():
            for record in record_package["records"]:
                for release in record["releases"]:
                    yield self.build_request(release["url"], formatter=components(-1))
