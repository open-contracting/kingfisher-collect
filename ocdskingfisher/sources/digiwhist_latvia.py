from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistLatviaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Latvia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_latvia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/LV_ocds_data.json.tar.gz'
