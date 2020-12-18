from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistSpain(DigiwhistBase):
    name = 'digiwhist_spain'
    start_urls = ['https://opentender.eu/data/files/ES_ocds_data.json.tar.gz']
