from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistMaltaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Malta'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_malta'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/MT_ocds_data.json.tar.gz'
