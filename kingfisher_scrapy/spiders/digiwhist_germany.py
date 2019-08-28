from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistGermanyRepublic(DigiwhistBase):
    name = 'digiwhist_germany'
    start_urls = ['https://opentender.eu/data/files/DE_ocds_data.json.tar.gz']
