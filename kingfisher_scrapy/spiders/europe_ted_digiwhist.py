from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class EuropeTEDDigiwhist(DigiwhistBase):
    name = 'europe_ted_digiwhist'
    start_urls = ['https://opentender.eu/data/files/TED_ocds_data.json.tar.gz']
