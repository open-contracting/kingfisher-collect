from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class HungaryDigiwhist(DigiwhistBase):
    name = 'hungary_digiwhist'
    start_urls = ['https://opentender.eu/data/files/HU_ocds_data.json.tar.gz']
