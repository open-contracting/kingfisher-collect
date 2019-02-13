from ocdskingfisher import util
from ocdskingfisher.base import Source
import hashlib


class MexicoGrupoAeroportoSource(Source):
    publisher_name = 'Mexico Grupo Aeroporto'
    url = 'https://datos.gob.mx/busca/organization/gacm'
    source_id = 'mexico_grupo_aeroporto'

    def gather_all_download_urls(self):
        r = util.get_url_request('https://datos.gob.mx/busca/api/3/action/package_search?q=organization:gacm&rows=500')
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        data = r.json()
        urls = []
        for result in data['result']['results']:
            for resource in result['resources']:
                if not self.sample or (self.sample and len(urls) < 10):
                    if resource['format'] == 'JSON' and \
                            resource['url'] != "http://datos.gob.mx/adela/api/v1/organizations/gacm/documents":
                        urls.append({
                            'url': resource['url'],
                            'filename': 'file-%s.json' % hashlib.md5(resource['url'].encode('utf-8')).hexdigest(),
                            'data_type': 'release_package_list' if resource['name'] == "CONCENTRADO ARCHIVO JSON" else 'release_package',
                        })
        return urls
