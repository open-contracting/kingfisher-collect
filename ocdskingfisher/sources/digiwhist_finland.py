from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistFinlandRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Finland'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_finland'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/FI_ocds_data.json.tar.gz'
