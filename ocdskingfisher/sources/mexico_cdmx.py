from ocdskingfisher import util
from ocdskingfisher.base import Source


class MexicoCDMXSource(Source):
    """
    API documentation: http://www.contratosabiertos.cdmx.gob.mx/datos-abiertos/documentacion-api-contratos
    """

    publisher_name = 'Mexico CDMX'
    url = 'http://www.contratosabiertos.cdmx.gob.mx'
    source_id = 'mexico_cdmx'

    def gather_all_download_urls(self):
        r = util.get_url_request('http://www.contratosabiertos.cdmx.gob.mx/api/contratos/todos')
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        datas = r.json()
        out = []
        for data in datas:
            if not self.sample or (self.sample and len(out) < 10):
                out.append({
                    'url': data['uri'],
                    'filename': 'id%s.json' % data['id'],
                    'data_type': 'release_package',
                })
        return out
