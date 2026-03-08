# https://github.com/scrapy/scrapy/blob/e02ad08672a5946f659acf4874c4a315e7886346/scrapy/http/response/text.py#L79-L83
import orjson
from scrapy.http import TextResponse

_NONE = object()


class JSONResponse(TextResponse):
    _cached_decoded_json = _NONE

    def json(self):
        if self._cached_decoded_json is _NONE:
            self._cached_decoded_json = orjson.loads(self.body)
        return self._cached_decoded_json
