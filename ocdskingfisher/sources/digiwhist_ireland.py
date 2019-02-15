from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistIrelandRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Ireland'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_ireland'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/IE_ocds_data.json.tar.gz'
