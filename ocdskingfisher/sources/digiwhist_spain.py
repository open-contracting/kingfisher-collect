from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistSpainRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Spain'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_spain'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/ES_ocds_data.json.tar.gz'
