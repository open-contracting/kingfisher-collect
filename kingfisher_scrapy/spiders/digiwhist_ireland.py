from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistIrelandRepublic(DigiwhistBase):
    name = 'digiwhist_ireland'
    start_urls = ['https://opentender.eu/data/files/IE_ocds_data.json.tar.gz']
