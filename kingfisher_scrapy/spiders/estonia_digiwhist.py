from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class EstoniaDigiwhist(DigiwhistBase):
    name = 'estonia_digiwhist'
    start_urls = ['https://opentender.eu/data/files/EE_ocds_data.json.tar.gz']
