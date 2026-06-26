# https://docs.scrapy.org/en/latest/topics/download-handlers.html
import asyncio
import logging

from curl_cffi import requests
from curl_cffi.const import CurlIpResolve, CurlOpt
from curl_cffi.requests.exceptions import RequestException, Timeout
from scrapy.exceptions import DownloadFailedError, DownloadTimeoutError
from scrapy.http import Headers
from scrapy.responsetypes import responsetypes

logger = logging.getLogger(__name__)


class CurlImpersonateDownloadHandler:
    """
    A download handler that uses ``curl_cffi`` to impersonate a browser's TLS/JA3 fingerprint.

    Some sites use an anti-bot service (like Cloudflare) that rejects Scrapy's default Twisted client by its TLS/JA3
    fingerprint. ``curl_cffi`` reproduces a real browser's fingerprint.

    To use it for a spider, override the ``https`` (and/or ``http``) handler in the spider's ``custom_settings``:

    .. code-block:: python

       custom_settings = {
           "DOWNLOAD_HANDLERS": {
               "https": "kingfisher_scrapy.downloadhandlers.CurlImpersonateDownloadHandler",
           },
       }

    And optionally:

    -  Set the ``CURL_IMPERSONATE`` setting to a `browser profile <https://github.com/lexiforest/curl_cffi#sessions>`__.
       Choose a specific version (like ``"chrome146"``) for a consistent fingerprint across ``curl_cffi`` upgrades.
    -  Set the ``CURL_IP_VERSION`` setting to ``"4"`` or ``"6"`` for a consistent version across requests. If unset,
       ``curl_cffi`` chooses.
    """

    lazy = True

    IP_RESOLVE = {"4": CurlIpResolve.V4, "6": CurlIpResolve.V6}

    def __init__(self, settings):
        self.impersonate = settings.get("CURL_IMPERSONATE") or "chrome"
        self.ip_resolve = self.IP_RESOLVE.get(settings.get("CURL_IP_VERSION"))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    async def download_request(self, request):
        return await asyncio.to_thread(self._download, request)

    def _download(self, request):
        kwargs = {
            "method": request.method,
            "url": request.url,
            # curl_cffi expects a plain dict of strings. Join multi-valued headers like Scrapy's HTTP/1.1 handler.
            "headers": {key.decode(): b", ".join(values).decode() for key, values in request.headers.items()},
            "data": request.body,
            "impersonate": self.impersonate,
            # Let Scrapy's RedirectMiddleware handle redirects.
            "allow_redirects": False,
        }
        # Scrapy sets the download_timeout meta from the DOWNLOAD_TIMEOUT setting.
        if timeout := request.meta.get("download_timeout"):
            kwargs["timeout"] = timeout
        # Set by HttpProxyMiddleware, which the spider enables with HTTPPROXY_ENABLED.
        if proxy := request.meta.get("proxy"):
            kwargs["proxies"] = {"http": proxy, "https": proxy}
        # Force the IP version, so that the request uses, e.g., the same version that solved a Cloudflare challenge.
        if self.ip_resolve is not None:
            kwargs["curl_options"] = {CurlOpt.IPRESOLVE: self.ip_resolve}

        try:
            response = requests.request(**kwargs)
        # Translate curl_cffi exceptions to Scrapy exceptions.
        except Timeout as exception:  # Timeout is a subclass of RequestException.
            raise DownloadTimeoutError(str(exception)) from exception
        except RequestException as exception:
            raise DownloadFailedError(str(exception)) from exception

        # curl_cffi already decompressed the body, so drop Content-Encoding (and the now-incorrect Content-Length), to
        # stop Scrapy's HttpCompressionMiddleware from trying to decompress it again (raising BadGzipFile).
        headers = Headers(
            [
                (name, value)
                for name, value in response.headers.multi_items()
                if name.lower() not in ("content-encoding", "content-length")
            ]
        )
        response_class = responsetypes.from_args(headers=headers, url=response.url, body=response.content)
        return response_class(
            url=response.url,
            status=response.status_code,
            headers=headers,
            body=response.content,
            request=request,
        )
