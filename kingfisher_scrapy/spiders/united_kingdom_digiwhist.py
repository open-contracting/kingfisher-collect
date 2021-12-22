from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class UnitedKingdomDigiwhist(DigiwhistBase):
    name = 'united_kingdom_digiwhist'
    start_urls = ['https://opentender.eu/data/files/UK_ocds_data.json.tar.gz']
