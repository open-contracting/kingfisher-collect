from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistItaly(DigiwhistBase):
    name = 'digiwhist_italy'
    start_urls = ['https://opentender.eu/data/files/IT_ocds_data.json.tar.gz']
