from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class RomaniaDigiwhist(DigiwhistBase):
    name = 'romania_digiwhist'
    start_urls = ['https://opentender.eu/data/files/RO_ocds_data.json.tar.gz']
