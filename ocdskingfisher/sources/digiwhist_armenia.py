from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistArmeniaSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Armenia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_armenia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/AM_ocds_data.json.tar.gz'
