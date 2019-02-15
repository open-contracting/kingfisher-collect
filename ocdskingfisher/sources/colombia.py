import json

from ocdskingfisher.base import Source
from ocdskingfisher.util import save_content


class ColombiaSource(Source):
    """
    API documentation and bulk downloads: https://www.colombiacompra.gov.co/transparencia/gestion-documental/datos-abiertos
    """

    publisher_name = 'Colombia'
    url = 'https://api.colombiacompra.gov.co'
    source_id = 'colombia'

    def gather_all_download_urls(self):
        return [{
            'url': 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases?page=1',
            'filename': 'page-1-.json',
            'data_type': 'release_package',
        }]

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'release_package':

            save_content_response = save_content(data['url'], file_path)
            if save_content_response.errors:
                return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

            additional = []

            with open(file_path) as f:
                json_data = json.load(f)

            page = int(filename.split('-')[1])
            if 'links' in json_data and 'next' in json_data['links'] and (not self.sample or page < 3):
                page += 1
                additional.append({
                    'url': json_data['links']['next'],
                    'filename': 'page-%d-.json' % page,
                    'data_type': 'release_package',
                })
            return self.SaveUrlResult(additional_files=additional, warnings=save_content_response.warnings)
