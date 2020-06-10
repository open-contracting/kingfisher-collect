from kingfisher_scrapy.spiders.paraguay_dncp_base import ParaguayDNCPBaseSpider


class ParaguayDNCPRecords(ParaguayDNCPBaseSpider):
    """
    Swagger API documentation
      https://contrataciones.gov.py/datos/api/v3/doc
    Spider arguments
      sample
        Download only 10 records.
      from_date
        Download only records from this date onward (YYYY-MM-DDTHH:mm:ss format).
        If `from_date` is not provided, defaults to '2010-01-01T00:00:00'.
    Environment variables
      KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN
        To get an API account and request token go to https://contrataciones.gov.py/datos/adm/login.
    """
    name = 'paraguay_dncp_records'
    data_type = 'record_package'
    skip_latest_release_date = 'Already covered by paraguay_dncp_releases'

    def get_files_to_download(self, content):
        for record in content['records']:
            yield f"{self.base_url}/ocds/record/{record['ocid']}"
