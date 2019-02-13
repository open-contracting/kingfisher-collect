from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistPortugalRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Portugal'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_portugal'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/PT_ocds_data.json.tar.gz'
