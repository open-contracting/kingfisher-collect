from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class LuxembourgDigiwhist(DigiwhistBase):
    name = 'luxembourg_digiwhist'
    start_urls = ['https://opentender.eu/data/files/LU_ocds_data.json.tar.gz']
