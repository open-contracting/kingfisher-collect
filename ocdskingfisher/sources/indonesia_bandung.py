from ocdskingfisher.base import Source
from ocdskingfisher import util
import json


class IndonesiaBandungSource(Source):
    publisher_name = 'Indonesia Bandung'
    url = 'https://birms.bandung.go.id'
    source_id = 'indonesia_bandung'

    def gather_all_download_urls(self):

        if self.sample:
            return [{
                'url': 'https://birms.bandung.go.id/beta/api/packages/year/2017?page=1',
                'filename': 'sample.json',
                'data_type': 'meta',
                'priority': 10
            }]

        out = []

        for year in range(2013, 2019):
            url = 'https://birms.bandung.go.id/beta/api/packages/year/{}'.format(year)
            response, errors = util.get_url_request(url, verify_ssl=False)
            if errors:
                raise Exception(errors)
            data = response.json()

            last_page = data['last_page']
            for page in range(1, last_page+1):
                out.append({
                    'url': 'https://birms.bandung.go.id/beta/api/packages/year/{}?page={}'.format(year, page),
                    'filename': 'year{}page{}.json'.format(year, page),
                    'data_type': 'meta',
                    'priority': 10
                })

        return out

    def save_url(self, filename, data, file_path):
        if data['data_type'] == 'meta':

            response, errors = util.get_url_request(data['url'], verify_ssl=False)
            if errors:
                return self.SaveUrlResult(errors=errors)

            data = json.loads(response.text)

            additional = []

            if "data" in data.keys():

                # Sometimes it's a dict, sometimes it's a list.
                if isinstance(data['data'], dict):
                    data['data'] = data['data'].values()

                for data_item in data["data"]:
                    if not self.sample or (self.sample and len(additional) < 10):
                        additional.append({
                                        'url': data_item['uri'],
                                        'filename': '{}.json'.format(data_item['ocid']),
                                        'data_type': 'release_package',
                                        'priority': 1,
                                    })

            return self.SaveUrlResult(additional_files=additional)

        else:
            save_content_response = util.save_content(data['url'], file_path, verify_ssl=False)
            return self.SaveUrlResult(errors=save_content_response.errors, warnings=save_content_response.warnings)
