from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class PolandDigiwhist(DigiwhistBase):
    name = 'poland_digiwhist'
    start_urls = ['https://opentender.eu/data/files/PL_ocds_data.json.tar.gz']
