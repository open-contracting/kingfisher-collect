from ocdskingfisher.base import Source


class TestFailSource(Source):
    publisher_name = 'test_fail'
    url = 'https://www.open-contracting.org'
    source_id = 'test_fail'

    def gather_all_download_urls(self):
        return [
            {
                'url': 'https://raw.githubusercontent.com/open-contracting/sample-data/master/fictional-example/1.1/ocds-213czf-000-00001-01-planning.json',
                'filename': 'fine.json',
                'data_type': 'release_package',
            },
            {
                'url': 'https://www.open-contracting.org/i-want-a-kitten',
                'filename': '404.json',
                'data_type': 'release_package',
            },
            {
                'url': 'http://httpstat.us/500',
                'filename': '500.json',
                'data_type': 'release_package',
            },
            {
                'url': 'http://httpstat.us/502',
                'filename': '502.json',
                'data_type': 'release_package',
            },
        ]
