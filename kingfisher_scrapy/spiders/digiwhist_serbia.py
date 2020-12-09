from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistSerbia(DigiwhistBase):
    name = 'digiwhist_serbia'
    start_urls = ['https://opentender.eu/data/files/RS_ocds_data.json.tar.gz']
