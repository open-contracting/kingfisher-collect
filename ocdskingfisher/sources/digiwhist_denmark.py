from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistDenmarkRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Denmark'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_denmark'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/DK_ocds_data.json.tar.gz'
