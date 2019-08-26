from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistSwedenRepublic(DigiwhistBase):
    name = 'digiwhist_sweden'
    start_urls = ['https://opentender.eu/data/files/SE_ocds_data.json.tar.gz']
