from kingfisher_scrapy.spiders.paraguay_dncp_base import ParaguayDNCPBaseSpider


class ParaguayDNCPRecords(ParaguayDNCPBaseSpider):
    """
    Domain
      Dirección Nacional de Contrataciones Públicas (DNCP)
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format). Defaults to '2010-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format). Defaults to today.
    Environment variables
      KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN
        To get an API account and request token go to https://contrataciones.gov.py/datos/adm/login.
    Swagger API documentation
      https://contrataciones.gov.py/datos/api/v3/doc
    """
    name = 'paraguay_dncp_records'
    data_type = 'record_package'
    skip_pluck = 'Already covered (see code for details)'  # paraguay_dncp_releases

    def get_files_to_download(self, content):
        for record in content['records']:
            yield f"{self.base_url}/ocds/record/{record['ocid']}"
