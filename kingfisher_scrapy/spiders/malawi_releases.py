from kingfisher_scrapy.spiders.malawi_base import MalawiBase


class MalawiReleases(MalawiBase):
    """
    Domain
      Malawi National Electronic Procurement System (MANEPS)
    Caveats
      The get-records endpoint's response time increases with the number of results skipped, and requests time out
      with an HTTP 504 error after 60 seconds. As such, only about the first 6,000 of 28,000 results can be paginated,
      as of July 2026.
    Swagger API documentation
      https://maneps.mw/rms/api/docs
    """

    name = "malawi_releases"

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # malawi_records

    # SimpleSpider
    data_type = "release_package"
