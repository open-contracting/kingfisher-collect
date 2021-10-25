from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class FinlandDigiwhist(DigiwhistBase):
    name = 'finland_digiwhist'
    start_urls = ['https://opentender.eu/data/files/FI_ocds_data.json.tar.gz']
