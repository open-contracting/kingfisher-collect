from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase


class NigeriaBudeshiRecords(NigeriaBudeshiBase):
    """
    API documentation
      https://budeshi.ng/Api
    """
    name = 'nigeria_budeshi_records'
    data_type = 'record_package'
    url = 'https://budeshi.ng/api/record/{}'
