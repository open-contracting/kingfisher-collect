from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistGreeceRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Greece'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_greece'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/GR_ocds_data.json.tar.gz'
