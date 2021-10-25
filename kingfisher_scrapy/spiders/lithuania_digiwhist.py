from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class LithuaniaDigiwhist(DigiwhistBase):
    name = 'lithuania_digiwhist'
    start_urls = ['https://opentender.eu/data/files/LT_ocds_data.json.tar.gz']
