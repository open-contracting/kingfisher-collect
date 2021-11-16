from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class GermanyDigiwhist(DigiwhistBase):
    name = 'germany_digiwhist'
    start_urls = ['https://opentender.eu/data/files/DE_ocds_data.json.tar.gz']
