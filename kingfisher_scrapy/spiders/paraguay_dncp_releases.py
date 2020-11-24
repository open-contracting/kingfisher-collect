from kingfisher_scrapy.spiders.paraguay_dncp_base import ParaguayDNCPBaseSpider


class ParaguayDNCPReleases(ParaguayDNCPBaseSpider):
    """
    Domain
      Dirección Nacional de Contrataciones Públicas (DNCP)
    Spider arguments
      from_date
        Download only releases from this release.date onward (YYYY-MM-DDTHH:mm:ss format).
        If ``until_date`` is provided, defaults to '2010-01-01T00:00:00'.
      until_date
        Download only releases until this date (YYYY-MM-DDTHH:mm:ss format).
        If ``from_date`` is provided, defaults to today.
    Environment variables
      KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN
        To get an API account and request token go to https://contrataciones.gov.py/datos/adm/login.
    Swagger API documentation
      https://contrataciones.gov.py/datos/api/v3/doc
    """
    name = 'paraguay_dncp_releases'
    data_type = 'release_package'

    def get_files_to_download(self, content):
        for record in content['records']:
            for release in record['releases']:
                yield release['url']
