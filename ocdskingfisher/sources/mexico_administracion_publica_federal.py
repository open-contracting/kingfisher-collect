from ocdskingfisher import util
from ocdskingfisher.base import Source


class MexicoAdministracionPublicaFederal(Source):
    """
    Bulk downloads: https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    """

    publisher_name = 'Mexico Administracion Publica Fedaral'
    url = 'https://api.datos.gob.mx/v1/contratacionesabiertas'
    source_id = 'mexico_administracion_publica_federal'

    def gather_all_download_urls(self):
        url = 'https://api.datos.gob.mx/v1/contratacionesabiertas?page=%d'
        if self.sample:
            return [{
                'url': url % 1,
                'filename': 'sample.json',
                'data_type': 'record_package_list_in_results',
            }]

        r = util.get_url_request(url % 2)
        if r[1]:
            raise Exception(r[1])
        r = r[0]
        data = r.json()
        total = data['pagination']['total']
        page = 1
        out = []
        limit = data['pagination']['pageSize']
        while ((page-1)*limit) < total:
            out.append({
                'url': url % page,
                'filename': 'page%d.json' % page,
                'data_type': 'record_package_list_in_results',
            })
            page += 1
        return out
