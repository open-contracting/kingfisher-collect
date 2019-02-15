from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistSwitzerlandRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Switzerland'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_switzerland'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/CH_ocds_data.json.tar.gz'
