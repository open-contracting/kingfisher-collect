from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistAustriaSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Austria'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_austria'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/AT_ocds_data.json.tar.gz'
