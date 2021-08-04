from kingfisher_scrapy.spiders.nigeria_cross_river_base import NigeriaCrossRiverBase


class NigeriaCrossRiverRecords(NigeriaCrossRiverBase):
    """
    Domain
      Cross River Nigeria
    API documentation
      http://ocdsapi.dppib-crsgov.org/Help
    """
    name = 'nigeria_cross_river_state_records'

    # SimpleSpider
    data_type = 'record_package'

    def build_urls(self, date):
        pattern = self.base_url + 'getRecordPackage?year={0.year:d}&month={0.month:02d}'
        yield pattern.format(date)
