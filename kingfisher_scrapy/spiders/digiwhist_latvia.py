from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistLatviaRepublic(DigiwhistBase):
    name = 'digiwhist_latvia'
    start_urls = ['https://opentender.eu/data/files/LV_ocds_data.json.tar.gz']
