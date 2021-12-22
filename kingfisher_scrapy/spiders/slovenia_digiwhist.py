from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class SloveniaDigiwhist(DigiwhistBase):
    name = 'slovenia_digiwhist'
    start_urls = ['https://opentender.eu/data/files/SI_ocds_data.json.tar.gz']
