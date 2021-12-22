from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class SlovakiaDigiwhist(DigiwhistBase):
    name = 'slovakia_digiwhist'
    start_urls = ['https://opentender.eu/data/files/SK_ocds_data.json.tar.gz']
