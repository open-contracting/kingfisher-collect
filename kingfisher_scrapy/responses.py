import orjson
from scrapy.http import TextResponse
from scrapy.http.response.text import _NONE


class JSONResponse(TextResponse):
    # https://github.com/scrapy/scrapy/blob/47e25fbbb5ac3012c3cc6e88bd9ff79f3a61c2a5/scrapy/http/response/text.py#L86-L90
    def json(self):
        if self._cached_decoded_json is _NONE:
            self._cached_decoded_json = orjson.loads(self.body)
        return self._cached_decoded_json
