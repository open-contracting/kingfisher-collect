from kingfisher_scrapy.spiders.paraguay_dncp_base import ParaguayDNCPBaseSpider


class ParaguayDNCPRecords(ParaguayDNCPBaseSpider):
    name = 'paraguay_dncp_records'
    data_type = 'record_package'

    def get_files_to_download(self, content):
        for record in content['records']:
            yield '{}/ocds/record/{}'.format(self.base_url, record['ocid'])
