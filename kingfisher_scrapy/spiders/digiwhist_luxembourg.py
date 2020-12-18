from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistLuxembourg(DigiwhistBase):
    name = 'digiwhist_luxembourg'
    start_urls = ['https://opentender.eu/data/files/LU_ocds_data.json.tar.gz']
