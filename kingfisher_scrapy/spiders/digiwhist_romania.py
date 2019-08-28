from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistRomaniaRepublic(DigiwhistBase):
    name = 'digiwhist_romania'
    start_urls = ['https://opentender.eu/data/files/RO_ocds_data.json.tar.gz']
