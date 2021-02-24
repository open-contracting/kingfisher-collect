from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistTED(DigiwhistBase):
    name = 'digiwhist_ted'
    start_urls = ['https://opentender.eu/data/files/TED_ocds_data.json.tar.gz']
