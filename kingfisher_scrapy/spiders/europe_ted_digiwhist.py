from kingfisher_scrapy.spiders.government_transparency_institute_base import GovernmentTransparencyInstituteBase


class EuropeTEDDigiwhist(GovernmentTransparencyInstituteBase):
    name = 'europe_ted_digiwhist'
    country_code = 'ted'
    infix = 'json'  # https://opentender.eu/data/downloads/data-ted-json-json.zip
