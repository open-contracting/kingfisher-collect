from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class MexicoINAIBase(PeriodicSpider):
    # BaseSpider
    root_path = 'arrayReleasePackage.item'
    date_format = 'year'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    formatter = staticmethod(components(-1))
