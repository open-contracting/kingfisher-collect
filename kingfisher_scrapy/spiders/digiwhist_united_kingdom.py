from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistUnitedKingdom(DigiwhistBase):
    name = 'digiwhist_united_kingdom'
    start_urls = ['https://opentender.eu/data/files/UK_ocds_data.json.tar.gz']
