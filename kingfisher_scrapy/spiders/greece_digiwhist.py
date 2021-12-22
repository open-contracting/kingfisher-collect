from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class GreeceDigiwhist(DigiwhistBase):
    name = 'greece_digiwhist'
    start_urls = ['https://opentender.eu/data/files/GR_ocds_data.json.tar.gz']
