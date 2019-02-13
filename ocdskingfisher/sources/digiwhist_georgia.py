from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistGeorgiaRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Georgia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_georgia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/GE_ocds_data.json.tar.gz'
