from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class AustriaDigiwhist(DigiwhistBase):
    name = 'austria_digiwhist'
    start_urls = ['https://opentender.eu/data/files/AT_ocds_data.json.tar.gz']
