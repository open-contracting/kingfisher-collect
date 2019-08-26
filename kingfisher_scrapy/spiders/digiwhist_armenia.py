from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistArmenia(DigiwhistBase):
    name = 'digiwhist_armenia'
    start_urls = ['https://opentender.eu/data/files/AM_ocds_data.json.tar.gz']
