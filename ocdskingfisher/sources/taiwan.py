from ocdskingfisher.base import Source


class TaiwanSource(Source):
    """
    Bulk downloads: http://data.dsp.im/dataset/taiwan-open-contracting
    """

    publisher_name = 'Taiwan'
    url = 'http://data.dsp.im'
    source_id = 'taiwan'

    def gather_all_download_urls(self):
        return [
            {
                'url': 'http://data.dsp.im/dataset/963c0c3d-49ac-4a66-b8fa-f56c8166bb91/resource/0abbe767-c940-49fe-80d3-bd68268f508e/download/2014-02.json',
                'filename': '2014-02.json',
                'data_type': 'release_package',
            }
        ]
