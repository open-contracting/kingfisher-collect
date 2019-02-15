from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistBelgiumSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Belgium'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_belgium'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/BE_ocds_data.json.tar.gz'
