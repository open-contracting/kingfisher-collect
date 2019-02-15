from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistSerbiaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Serbia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_serbia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/RS_ocds_data.json.tar.gz'
