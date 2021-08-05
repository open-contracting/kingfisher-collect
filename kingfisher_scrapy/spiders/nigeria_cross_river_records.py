from kingfisher_scrapy.spiders.nigeria_cross_river_base import NigeriaCrossRiverBase


class NigeriaCrossRiverRecords(NigeriaCrossRiverBase):
    """
    Domain
      Cross River Nigeria
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2020-02'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      http://ocdsapi.dppib-crsgov.org/Help
    """
    name = 'nigeria_cross_river_state_records'

    # SimpleSpider
    data_type = 'record_package'

    def build_urls(self, date):
        pattern = self.base_url + 'getRecordPackage?year={0.year:d}&month={0.month:02d}'
        yield pattern.format(date)
