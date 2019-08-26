from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class DigiwhistNetherlandsRepublic(DigiwhistBase):
    name = 'digiwhist_netherlands'
    start_urls = ['https://opentender.eu/data/files/NL_ocds_data.json.tar.gz']
