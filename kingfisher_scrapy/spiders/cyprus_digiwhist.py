from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class CyprusDigiwhist(DigiwhistBase):
    name = 'cyprus_digiwhist'
    start_urls = ['https://opentender.eu/data/files/CY_ocds_data.json.tar.gz']
