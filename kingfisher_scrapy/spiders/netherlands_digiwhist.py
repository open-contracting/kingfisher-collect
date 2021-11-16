from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class NetherlandsDigiwhist(DigiwhistBase):
    name = 'netherlands_digiwhist'
    start_urls = ['https://opentender.eu/data/files/NL_ocds_data.json.tar.gz']
