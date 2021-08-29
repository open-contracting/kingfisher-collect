from urllib.parse import urljoin

import treq


class Client:
    def __init__(self, url, key):
        self.url = url
        self.headers = {'Authorization': f'ApiKey {key}'}

    def create_file(self, data, files):
        return self._post('/api/v1/submit/file/', data, files=files)

    def create_file_item(self, data):
        return self._post('/api/v1/submit/item/', data)

    def create_file_error(self, data):
        return self._post('/api/v1/submit/file_errors/', data)

    def end_collection_store(self, data):
        return self._post('/api/v1/submit/end_collection_store/', data)

    def _post(self, path, data, **kwargs):
        return treq.post(urljoin(self.url, path), headers=self.headers, data=data, **kwargs)
