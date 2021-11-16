from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class ItalyDigiwhist(DigiwhistBase):
    name = 'italy_digiwhist'
    start_urls = ['https://opentender.eu/data/files/IT_ocds_data.json.tar.gz']
