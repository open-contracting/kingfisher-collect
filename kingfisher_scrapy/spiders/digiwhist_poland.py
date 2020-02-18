from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistPolandRepublic(DigiwhistBase):
    name = 'digiwhist_poland'
    start_urls = ['https://opentender.eu/data/files/PL_ocds_data.json.tar.gz']
    download_maxsize = 0
