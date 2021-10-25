from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class SwedenDigiwhist(DigiwhistBase):
    name = 'sweden_digiwhist'
    start_urls = ['https://opentender.eu/data/files/SE_ocds_data.json.tar.gz']
