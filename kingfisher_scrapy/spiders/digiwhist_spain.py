from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistSpainRepublic(DigiwhistBase):
    name = 'digiwhist_spain'
    start_urls = ['https://opentender.eu/data/files/ES_ocds_data.json.tar.gz']
