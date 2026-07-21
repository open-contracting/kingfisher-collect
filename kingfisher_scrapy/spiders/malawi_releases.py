from kingfisher_scrapy.spiders.malawi_base import MalawiBase


class MalawiReleases(MalawiBase):
    """
    Domain
      Malawi National Electronic Procurement System (MANEPS)
    Swagger API documentation
      https://maneps.mw/rms/api/docs
    """

    name = "malawi_releases"

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # malawi_records

    # SimpleSpider
    data_type = "release_package"
