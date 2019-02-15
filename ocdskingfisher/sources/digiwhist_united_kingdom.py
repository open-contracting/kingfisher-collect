from ocdskingfisher.sources.digiwhist_base import DigiwhistBaseSource


class DigiwhistUnitedKingdomRepublicSource(DigiwhistBaseSource):
    publisher_name = 'Digiwhist United Kingdom'
    url = 'https://opentender.eu/download'
    source_id = 'digiwhist_united_kingdom'

    def get_data_url(self):
        return 'https://opentender.eu/data/files/UK_ocds_data.json.tar.gz'
