from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistCzechRepublic(DigiwhistBase):
    name = 'digiwhist_czech_republic'
    start_urls = ['https://opentender.eu/data/files/CZ_ocds_data.json.tar.gz']
