from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class CzechRepublicDigiwhist(DigiwhistBase):
    name = 'czech_republic_digiwhist'
    start_urls = ['https://opentender.eu/data/files/CZ_ocds_data.json.tar.gz']
