from kingfisher_scrapy.spiders.government_transparency_institute_base import GovernmentTransparencyInstituteBase


class PolandDigiwhist(GovernmentTransparencyInstituteBase):
    name = "poland_digiwhist"

    # GovernmentTransparencyInstituteBase
    country_code = "pl"
    infix = "json"  # https://opentender.eu/pl/download
