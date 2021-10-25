from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DenmarkDigiwhist(DigiwhistBase):
    name = 'denmark_digiwhist'
    start_urls = ['https://opentender.eu/data/files/DK_ocds_data.json.tar.gz']
