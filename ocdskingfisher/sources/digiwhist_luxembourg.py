from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistLuxembourgRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Luxembourg'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_luxembourg'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/LU_ocds_data.json.tar.gz'
