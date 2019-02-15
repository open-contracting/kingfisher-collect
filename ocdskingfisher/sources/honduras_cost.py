from ocdskingfisher.base import Source


class HondurasCoSTSource(Source):
    publisher_name = 'Honduras CoST'
    url = 'http://app.sisocs.org/protected/ocdsShow/'
    source_id = 'honduras_cost'

    def gather_all_download_urls(self):
        return [
            {
                'url': 'http://67.207.88.38:8080/sisocs/records',
                'filename': '2014-02.json',
                'data_type': 'record_package',
            }
        ]
