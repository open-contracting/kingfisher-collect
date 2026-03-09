from kingfisher_scrapy.spiders.government_transparency_institute_base import GovernmentTransparencyInstituteBase


class FinlandDigiwhist(GovernmentTransparencyInstituteBase):
    name = "finland_digiwhist"

    # GovernmentTransparencyInstituteBase
    country_code = "fi"
