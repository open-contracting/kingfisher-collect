from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistGreece(DigiwhistBase):
    name = 'digiwhist_greece'
    start_urls = ['https://opentender.eu/data/files/GR_ocds_data.json.tar.gz']
