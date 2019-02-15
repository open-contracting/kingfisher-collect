from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistSlovakiaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Slovakia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_slovakia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/SK_ocds_data.json.tar.gz'
