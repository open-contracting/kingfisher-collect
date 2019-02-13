from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistCyprusSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Cyprus'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_cyprus'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/CY_ocds_data.json.tar.gz'
