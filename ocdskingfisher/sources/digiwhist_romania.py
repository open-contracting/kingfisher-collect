from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistRomaniaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Romania'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_romania'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/RO_ocds_data.json.tar.gz'
