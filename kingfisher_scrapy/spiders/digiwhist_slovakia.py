from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistSlovakia(DigiwhistBase):
    name = 'digiwhist_slovakia'
    start_urls = ['https://opentender.eu/data/files/SK_ocds_data.json.tar.gz']
