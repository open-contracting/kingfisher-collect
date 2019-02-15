from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistIcelandRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Iceland'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_iceland'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/IS_ocds_data.json.tar.gz'
