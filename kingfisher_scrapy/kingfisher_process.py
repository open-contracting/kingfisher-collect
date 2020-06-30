import requests


class Client:
    def __init__(self, url, key):
        self.url = url
        self.key = key

    def create_file(self, data, files):
        return self._post('/api/v1/submit/file/', data, files=files)

    def create_file_item(self, data):
        return self._post('/api/v1/submit/item/', data)

    def create_file_error(self, data):
        return self._post('/api/v1/submit/file_errors/', data)

    def end_collection_store(self, data):
        return self._post('/api/v1/submit/end_collection_store/', data)

    def _post(self, path, data, **kwargs):
        return requests.post(self.url + path, headers={'Authorization': 'ApiKey ' + self.key}, data=data,
                             proxies={'http': None, 'https': None}, **kwargs)
