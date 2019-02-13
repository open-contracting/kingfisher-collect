from io import BytesIO
from zipfile import ZipFile

import requests

from ocdskingfisher.base import Source
from ocdskingfisher.util import get_url_request

REQUEST_TOKEN = '06034873-f3e1-47b8-8bfb-45b11b3fc83d'
CLIENT_SECRET = 'e606642e20667a6b7b46b9644ce40a85d11a84da173d4d26f65cd5826121ec01'


class ParaguayHaciendaSource(Source):
    publisher_name = 'Paraguay Hacienda'
    url = 'https://datos.hacienda.gov.py/'
    source_id = 'paraguay_hacienda'

    def gather_all_download_urls(self):
        release_package_ids = []

        for year in range(2011, (2012 if self.sample else 2018)):
            release_package_ids += self.get_tender_ids(year)

        release_package_ids = set(release_package_ids)
        release_package_ids = list(release_package_ids)

        if self.sample:
            release_package_ids = release_package_ids[:5]

        out = []
        for release_package_id in release_package_ids:
            out.append({
                'url': 'https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/ocds/release-package/%s' %
                       release_package_id,
                'filename': 'release-%s.json' % release_package_id,
                'data_type': 'release_package',
            })

        return out

    @staticmethod
    def get_tender_ids(year):
        url = 'https://datos.hacienda.gov.py/odmh-core/rest/cdp/datos/cdp_%s.zip' % year
        resp = requests.get(url).content
        zipfile = ZipFile(BytesIO(resp))
        ids = []
        for line in zipfile.open('cdp_%s.csv' % year).readlines():
            line = str(line).split(',')
            id = line[-4].replace('"', '').split('/')[-1]
            if id is not '' and not(id == 'apiDNCP'):
                ids.append(id)
        return ids

    def save_url(self, filename, data, file_path):
        errors = self.save_content(data['url'], file_path, headers={"Authorization": self.get_access_token()})
        return self.SaveUrlResult(errors=errors)

    def save_content(self, url, filepath, headers=None):
        request, errors = get_url_request(url, stream=True, headers=headers)
        if any('Request exception (Code %s)' % 401 in s for s in errors):
            self.access_token = None
            errors = self.save_content(url, filepath, headers={"Authorization": self.get_access_token()})
        if not request:
            return errors

        try:
            with open(filepath, 'wb') as f:
                for chunk in request.iter_content(1024 ^ 2):
                    f.write(chunk)
            return []
        except Exception as e:
            return [str(e)]

    access_token = None

    def get_access_token(self):
        if self.access_token:
            return self.access_token
        correct = False
        token = ''
        while not correct:
            r = requests.post("https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/auth/token",
                              headers={"Authorization": REQUEST_TOKEN}, json={"clientSecret": "%s" % CLIENT_SECRET})
            try:
                token = r.json()['accessToken']
                correct = True
            except requests.exceptions.RequestException:
                correct = False
        self.access_token = token
        return token
