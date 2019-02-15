from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistCzechRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Czech Republic'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_czech_republic'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/CZ_ocds_data.json.tar.gz'
