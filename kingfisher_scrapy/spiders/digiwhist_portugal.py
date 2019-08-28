from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistPortugalRepublic(DigiwhistBase):
    name = 'digiwhist_portugal'
    start_urls = ['https://opentender.eu/data/files/PT_ocds_data.json.tar.gz']
