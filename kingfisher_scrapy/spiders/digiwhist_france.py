from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistFrance(DigiwhistBase):
    name = 'digiwhist_france'
    start_urls = ['https://opentender.eu/data/files/FR_ocds_data.json.tar.gz']
