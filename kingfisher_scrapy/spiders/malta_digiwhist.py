from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class MaltaDigiwhist(DigiwhistBase):
    name = 'malta_digiwhist'
    start_urls = ['https://opentender.eu/data/files/MT_ocds_data.json.tar.gz']
