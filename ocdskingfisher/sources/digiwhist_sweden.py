from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistSwedenRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Sweden'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_sweden'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/SE_ocds_data.json.tar.gz'
