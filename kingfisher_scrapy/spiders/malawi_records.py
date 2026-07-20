from kingfisher_scrapy.spiders.malawi_base import MalawiBase


class MalawiRecords(MalawiBase):
    """
    Domain
      Malawi National Electronic Procurement System (MANEPS)
    Caveats
      The get-records endpoint's response time increases with the number of results skipped, and requests time out
      with an HTTP 504 error after 60 seconds. As such, only a subset can be paginated.
    Swagger API documentation
      https://maneps.mw/rms/api/docs
    """

    name = "malawi_records"

    # SimpleSpider
    data_type = "record_package"
