from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistHungaryRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Hungary'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_hungary'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/HU_ocds_data.json.tar.gz'
