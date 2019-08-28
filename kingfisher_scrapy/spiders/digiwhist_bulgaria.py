from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistBulgaria(DigiwhistBase):
    name = 'digiwhist_bulgaria'
    start_urls = ['https://opentender.eu/data/files/BG_ocds_data.json.tar.gz']
