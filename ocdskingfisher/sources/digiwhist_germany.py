from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistGermanyRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Germany'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_germany'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/DE_ocds_data.json.tar.gz'
