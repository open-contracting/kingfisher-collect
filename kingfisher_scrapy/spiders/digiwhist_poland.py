from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistPoland(DigiwhistBase):
    name = 'digiwhist_poland'
    start_urls = ['https://opentender.eu/data/files/PL_ocds_data.json.tar.gz']
    # 20 minutes, 2.7GB file
    download_timeout = 1200
