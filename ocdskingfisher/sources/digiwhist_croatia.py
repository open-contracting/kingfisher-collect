from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistCroatiaSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist Croatia'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_croatia'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/HR_ocds_data.json.tar.gz'
