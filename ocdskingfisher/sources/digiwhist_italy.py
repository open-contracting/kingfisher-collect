from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistItalyRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Italy'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_italy'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/IT_ocds_data.json.tar.gz'
