from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class BulgariaDigiwhist(DigiwhistBase):
    name = 'bulgaria_digiwhist'
    start_urls = ['https://opentender.eu/data/files/BG_ocds_data.json.tar.gz']
