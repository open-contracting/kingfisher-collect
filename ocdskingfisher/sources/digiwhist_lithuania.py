from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistLithuaniaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Lithuania'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_lithuania'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/LT_ocds_data.json.tar.gz'
