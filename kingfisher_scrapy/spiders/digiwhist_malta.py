from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistMaltaRepublic(DigiwhistBase):
    name = 'digiwhist_malta'
    start_urls = ['https://opentender.eu/data/files/MT_ocds_data.json.tar.gz']
