from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistBelgium(DigiwhistBase):
    name = 'digiwhist_belgium'
    start_urls = ['https://opentender.eu/data/files/BE_ocds_data.json.tar.gz']
