from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistPolandRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Poland'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_poland'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/PL_ocds_data.json.tar.gz'
