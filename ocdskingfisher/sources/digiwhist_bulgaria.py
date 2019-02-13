from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistBulgariaSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Bulgaria'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_bulgaria'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/BG_ocds_data.json.tar.gz'
