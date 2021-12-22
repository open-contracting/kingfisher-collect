from kingfisher_scrapy.spiders.digiwhist_base import DigiwhistBase


class IrelandDigiwhist(DigiwhistBase):
    name = 'ireland_digiwhist'
    start_urls = ['https://opentender.eu/data/files/IE_ocds_data.json.tar.gz']
