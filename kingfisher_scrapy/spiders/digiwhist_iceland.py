from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistIcelandRepublic(DigiwhistBase):
    name = 'digiwhist_iceland'
    start_urls = ['https://opentender.eu/data/files/IS_ocds_data.json.tar.gz']
