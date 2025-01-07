from kingfisher_scrapy.spiders.government_transparency_institute_base import GovernmentTransparencyInstituteBase


class CzechRepublicDigiwhist(GovernmentTransparencyInstituteBase):
    name = 'czech_republic_digiwhist'
    country_code = 'cz'
    infix = 'json'  # https://opentender.eu/cz/download
