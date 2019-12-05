from kingfisher_scrapy.spiders.paraguay_base import ParaguayDNCPBaseSpider


class ParaguayDNCPRecords(ParaguayDNCPBaseSpider):
    name = 'paraguay_dncp_records'
    data_type = 'record_package'

    def get_files_to_download(self, content):
        for record in content['records']:
            url = 'http://beta.dncp.gov.py/datos/api/v3/doc/ocds/record/{}'.format(record['compiledRelease']['ocid'])
            file_name = '{}.json'.format(record['compiledRelease']['ocid'])
            yield url, file_name
