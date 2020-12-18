from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistDenmark(DigiwhistBase):
    name = 'digiwhist_denmark'
    start_urls = ['https://opentender.eu/data/files/DK_ocds_data.json.tar.gz']
