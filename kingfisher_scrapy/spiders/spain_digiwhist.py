from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class SpainDigiwhist(DigiwhistBase):
    name = 'spain_digiwhist'
    start_urls = ['https://opentender.eu/data/files/ES_ocds_data.json.tar.gz']
