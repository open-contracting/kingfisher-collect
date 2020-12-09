from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistHungary(DigiwhistBase):
    name = 'digiwhist_hungary'
    start_urls = ['https://opentender.eu/data/files/HU_ocds_data.json.tar.gz']
