from ocdskingfisher import util
from ocdskingfisher.base import Source


class UKContractsFinderSource(Source):
    """
    API documentation: https://www.gov.uk/government/publications/open-contracting
    """

    publisher_name = 'UK Contracts Finder'
    url = 'https://www.contractsfinder.service.gov.uk'
    source_id = 'uk_contracts_finder'

    def gather_all_download_urls(self):
        if self.sample:
            return [{
                'url': 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=1',
                'filename': 'page1.json',
                'data_type': 'release_package_list_in_results',
                'encoding': "ISO-8859-1"
            }]

        url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=1'
        r = util.get_url_request(url)
        if r[1]:
            raise Exception(r[1])
        r = r[0]

        data = r.json()
        total = data['maxPage']
        out = []
        for page in range(1, total+1):
            out.append({
                'url': 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=%d' % page,
                'filename': 'page%d.json' % page,
                'data_type': 'release_package_list_in_results',
                'encoding': "ISO-8859-1"
            })
        return out
