from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class IcelandDigiwhist(DigiwhistBase):
    name = 'iceland_digiwhist'
    start_urls = ['https://opentender.eu/data/files/IS_ocds_data.json.tar.gz']
