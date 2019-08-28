from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistCroatia(DigiwhistBase):
    name = 'digiwhist_croatia'
    start_urls = ['https://opentender.eu/data/files/HR_ocds_data.json.tar.gz']
