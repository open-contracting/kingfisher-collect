from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistSloveniaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Slovenia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_slovenia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/SI_ocds_data.json.tar.gz'
