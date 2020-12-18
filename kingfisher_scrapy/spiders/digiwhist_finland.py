from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistFinland(DigiwhistBase):
    name = 'digiwhist_finland'
    start_urls = ['https://opentender.eu/data/files/FI_ocds_data.json.tar.gz']
