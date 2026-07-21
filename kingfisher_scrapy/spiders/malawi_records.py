from kingfisher_scrapy.spiders.malawi_base import MalawiBase


class MalawiRecords(MalawiBase):
    """
    Domain
      Malawi National Electronic Procurement System (MANEPS)
    Swagger API documentation
      https://maneps.mw/rms/api/docs
    """

    name = "malawi_records"

    # SimpleSpider
    data_type = "record_package"
