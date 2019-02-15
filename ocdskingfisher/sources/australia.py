from ocdskingfisher.base import Source
from ocdskingfisher.util import save_content
import json
import hashlib


class AustraliaSource(Source):
    """
    """

    publisher_name = 'Australia'
    url = 'https://api.tenders.gov.au'
    source_id = 'australia'

    def gather_all_download_urls(self):

        if self.sample:
            return[{
                'url': "https://api.tenders.gov.au/ocds/findByDates/contractPublished/2018-01-01T00:00:00Z/2018-12-31T23:59:59Z",
                'filename': 'year-2018.json',
                'data_type': 'release_package',
            }]

        else:
            out = []
            for year in range(2004, 2020):
                url = "https://api.tenders.gov.au/ocds/findByDates/contractPublished/{}-01-01T00:00:00Z/{}-12-31T23:59:59Z".format(year, year)  # noqa
                out.append({
                    'url': url,
                    'filename': 'year-{}.json'.format(year),
                    'data_type': 'release_package',
                    'priority': year,
                })

            return out

    def save_url(self, filename, data, file_path):

        save_content_response = save_content(data['url'], file_path)
        if save_content_response.errors:
            return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)

        additional = []

        if not self.sample:

            with open(file_path) as f:
                json_data = json.load(f)

                if 'links' in json_data and 'next' in json_data['links'] and json_data['links']['next']:
                    additional.append({
                        'url': json_data['links']['next'],
                        'filename': 'page-%s.json' % hashlib.md5(json_data['links']['next'].encode('utf-8')).hexdigest(),
                        'data_type': 'release_package',
                        # We set priority the same so that all the requests for one year are done at the same time.
                        # Because of how this pages using cursors, it's probably best to get them as fast as possible.
                        'priority': data['priority'],
                    })

        return self.SaveUrlResult(additional_files=additional, warnings=save_content_response.warnings)
