from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistCyprus(DigiwhistBase):
    name = 'digiwhist_cyprus'
    start_urls = ['https://opentender.eu/data/files/CY_ocds_data.json.tar.gz']
