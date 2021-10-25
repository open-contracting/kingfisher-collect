from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class CroatiaDigiwhist(DigiwhistBase):
    name = 'croatia_digiwhist'
    start_urls = ['https://opentender.eu/data/files/HR_ocds_data.json.tar.gz']
