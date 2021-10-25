from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class PortugalDigiwhist(DigiwhistBase):
    name = 'portugal_digiwhist'
    start_urls = ['https://opentender.eu/data/files/PT_ocds_data.json.tar.gz']
