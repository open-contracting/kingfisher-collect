from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistSloveniaRepublic(DigiwhistBase):
    name = 'digiwhist_slovenia'
    start_urls = ['https://opentender.eu/data/files/SI_ocds_data.json.tar.gz']
