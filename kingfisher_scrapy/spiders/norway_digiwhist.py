from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class NorwayDigiwhist(DigiwhistBase):
    name = 'norway_digiwhist'
    start_urls = ['https://opentender.eu/data/files/NO_ocds_data.json.tar.gz']
