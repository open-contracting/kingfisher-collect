import http

from ocdskingfisher import util
from ocdskingfisher.base import Source


class MexicoINAISource(Source):
    publisher_name = 'Mexico > Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales'
    url = 'https://datos.gob.mx/busca/organization/inai'
    source_id = 'mexico_inai'

    def gather_all_download_urls(self):
        url = 'http://datos.gob.mx/busca/api/3/action/'
        url += 'package_search?q=organization:inai&rows=500'
        r = util.get_url_request(url)
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        data = r.json()
        out = []
        for result in data['result']['results']:
            for resource in result['resources']:
                if resource['format'] == 'JSON':
                    temp = resource['url'].split("//")[1]
                    conn = http.client.HTTPConnection(temp.split("/")[0])
                    name = temp.split("/")[1]
                    conn.request('HEAD', "/"+name)
                    response = conn.getresponse()
                    url = response.getheader('Location').replace("open?", "uc?export=download&")
                    out.append({
                        'url': url,
                        'filename': '{}.json'.format(name),
                        'data_type': 'release_package',
                        'encoding': 'utf-8-sig',  # ignore BOM
                    })
                    if self.sample:
                        return out
        return out
