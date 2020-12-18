from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistNorway(DigiwhistBase):
    name = 'digiwhist_norway'
    start_urls = ['https://opentender.eu/data/files/NO_ocds_data.json.tar.gz']
