from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class SwitzerlandDigiwhist(DigiwhistBase):
    name = 'switzerland_digiwhist'
    start_urls = ['https://opentender.eu/data/files/CH_ocds_data.json.tar.gz']
