from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistAustria(DigiwhistBase):
    name = 'digiwhist_austria'
    start_urls = ['https://opentender.eu/data/files/AT_ocds_data.json.tar.gz']
