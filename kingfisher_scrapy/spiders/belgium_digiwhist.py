from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class BelgiumDigiwhist(DigiwhistBase):
    name = 'belgium_digiwhist'
    start_urls = ['https://opentender.eu/data/files/BE_ocds_data.json.tar.gz']
