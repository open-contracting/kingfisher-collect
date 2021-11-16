from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class FranceDigiwhist(DigiwhistBase):
    name = 'france_digiwhist'
    start_urls = ['https://opentender.eu/data/files/FR_ocds_data.json.tar.gz']
