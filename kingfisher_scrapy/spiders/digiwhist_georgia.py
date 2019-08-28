from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistGeorgiaRepublic(DigiwhistBase):
    name = 'digiwhist_georgia'
    start_urls = ['https://opentender.eu/data/files/GE_ocds_data.json.tar.gz']
