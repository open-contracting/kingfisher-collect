from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistNorwayRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Norway'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_norway'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/NO_ocds_data.json.tar.gz'
