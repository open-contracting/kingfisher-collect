from kingfisher_scrapy.spiders.government_transparency_institute_base import GovernmentTransparencyInstituteBase


class EuropeTEDDigiwhist(GovernmentTransparencyInstituteBase):
    name = 'europe_ted_digiwhist'
    country_code = 'ted'

    # Unlike all others, data-ted-ocds-json.zip doesn't exist.
    base_url = 'https://opentender.eu/data/downloads/data-{}-json-json.zip'
