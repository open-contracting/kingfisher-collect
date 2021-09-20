from kingfisher_scrapy.spiders.nigeria_cross_river_base import NigeriaCrossRiverBase


class NigeriaCrossRiverRecords(NigeriaCrossRiverBase):
    """
    Domain
      Cross River State
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2019-08'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    API documentation
      http://ocdsapi.dppib-crsgov.org/Help
    """
    name = 'nigeria_cross_river_state_records'

    # SimpleSpider
    data_type = 'record_package'

    def build_url(self, date):
        return self.base_url + 'getRecordPackage?year={0.year:d}&month={0.month:02d}'.format(date)
