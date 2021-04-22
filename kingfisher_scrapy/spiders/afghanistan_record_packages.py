from kingfisher_scrapy.spiders.afghanistan_packages_base import AfghanistanPackagesBase


class AfghanistanRecordPackages(AfghanistanPackagesBase):
    """
    Domain
      Afghanistan Government Electronic & Open Procurement System (AGEOPS)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2018-12-15'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    API documentation
      https://ocds.ageops.net/
    """
    name = 'afghanistan_record_packages'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # afghanistan_release_packages

    # SimpleSpider
    data_type = 'record_package'

    base_url = 'https://ocds.ageops.net/api/ocds/record-package/dates'
