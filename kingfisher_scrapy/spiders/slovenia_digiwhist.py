from kingfisher_scrapy.spiders.government_transparency_institute_base import GovernmentTransparencyInstituteBase


class SloveniaDigiwhist(GovernmentTransparencyInstituteBase):
    name = "slovenia_digiwhist"

    # GovernmentTransparencyInstituteBase
    country_code = "si"
    infix = "json"  # https://opentender.eu/si/download
