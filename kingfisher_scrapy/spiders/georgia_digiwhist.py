from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class GeorgiaDigiwhist(DigiwhistBase):
    name = 'georgia_digiwhist'
    start_urls = ['https://opentender.eu/data/files/GE_ocds_data.json.tar.gz']
