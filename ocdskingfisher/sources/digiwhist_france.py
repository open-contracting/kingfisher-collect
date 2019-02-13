from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistFranceRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist France'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_france'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/FR_ocds_data.json.tar.gz'
