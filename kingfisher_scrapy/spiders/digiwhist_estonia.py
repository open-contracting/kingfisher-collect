from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistEstoniaRepublic(DigiwhistBase):
    name = 'digiwhist_estonia'
    start_urls = ['https://opentender.eu/data/files/EE_ocds_data.json.tar.gz']
