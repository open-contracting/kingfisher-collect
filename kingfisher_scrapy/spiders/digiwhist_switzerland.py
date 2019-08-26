from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistSwitzerlandRepublic(DigiwhistBase):
    name = 'digiwhist_switzerland'
    start_urls = ['https://opentender.eu/data/files/CH_ocds_data.json.tar.gz']
