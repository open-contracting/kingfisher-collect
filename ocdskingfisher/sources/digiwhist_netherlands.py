from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistNetherlandsRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Netherlands'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_netherlands'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/NL_ocds_data.json.tar.gz'
