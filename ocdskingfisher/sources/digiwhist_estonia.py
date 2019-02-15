from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistEstoniaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Estonia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_estonia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/EE_ocds_data.json.tar.gz'
