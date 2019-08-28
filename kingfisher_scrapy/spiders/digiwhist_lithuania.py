from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistLithuaniaRepublic(DigiwhistBase):
    name = 'digiwhist_lithuania'
    start_urls = ['https://opentender.eu/data/files/LT_ocds_data.json.tar.gz']
