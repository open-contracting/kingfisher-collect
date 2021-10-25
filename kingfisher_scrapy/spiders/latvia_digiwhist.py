from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class LatviaDigiwhist(DigiwhistBase):
    name = 'latvia_digiwhist'
    start_urls = ['https://opentender.eu/data/files/LV_ocds_data.json.tar.gz']
