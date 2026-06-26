import pytest
from curl_cffi.const import CurlIpResolve, CurlOpt
from curl_cffi.requests.exceptions import ConnectionError as CurlConnectionError
from curl_cffi.requests.exceptions import Timeout
from curl_cffi.requests.headers import Headers
from scrapy import Request
from scrapy.exceptions import DownloadFailedError, DownloadTimeoutError
from scrapy.http import Response
from scrapy.settings import Settings

from kingfisher_scrapy import downloadhandlers
from kingfisher_scrapy.downloadhandlers import CurlImpersonateDownloadHandler


class FakeResponse:
    def __init__(self, *, status_code=200, headers=None, content=b"", url="https://example.com"):
        self.status_code = status_code
        self.headers = Headers(headers or {"Content-Type": "application/zip"})
        self.content = content
        self.url = url


def handler(**settings):
    return CurlImpersonateDownloadHandler(Settings(settings))


def test_forwards_request(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return FakeResponse(status_code=200, headers={"Content-Type": "application/zip"}, content=b"PK\x03\x04")

    monkeypatch.setattr(downloadhandlers.requests, "request", fake_request)

    request = Request(
        "https://opentender.eu/data/downloads/data-ie-ocds-json.zip",
        headers={"User-Agent": "Mozilla/5.0 Chrome", "Cookie": "cf_clearance=abc"},
        meta={"download_timeout": 42, "proxy": "http://proxy:8080"},
    )

    response = handler(CURL_IMPERSONATE="chrome")._download(request)  # noqa: SLF001

    assert captured["impersonate"] == "chrome"
    assert captured["allow_redirects"] is False
    assert captured["timeout"] == 42
    assert captured["proxies"] == {"http": "http://proxy:8080", "https": "http://proxy:8080"}
    assert captured["headers"]["User-Agent"] == "Mozilla/5.0 Chrome"
    assert captured["headers"]["Cookie"] == "cf_clearance=abc"
    assert "curl_options" not in captured

    assert isinstance(response, Response)
    assert response.status == 200
    assert response.headers["Content-Type"] == b"application/zip"
    assert response.body == b"PK\x03\x04"


@pytest.mark.parametrize(("value", "expected"), [("4", CurlIpResolve.V4), ("6", CurlIpResolve.V6)])
def test_ip_version(monkeypatch, value, expected):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return FakeResponse(content=b"PK")

    monkeypatch.setattr(downloadhandlers.requests, "request", fake_request)

    handler(CURL_IP_VERSION=value)._download(Request("https://example.com"))  # noqa: SLF001

    assert captured["curl_options"] == {CurlOpt.IPRESOLVE: expected}


def test_ip_version_invalid(monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return FakeResponse(content=b"PK")

    monkeypatch.setattr(downloadhandlers.requests, "request", fake_request)

    handler(CURL_IP_VERSION="5")._download(Request("https://example.com"))  # noqa: SLF001

    assert "curl_options" not in captured


def test_download_timeout(monkeypatch):
    def fake_request(**kwargs):
        raise Timeout("timed out")

    monkeypatch.setattr(downloadhandlers.requests, "request", fake_request)

    with pytest.raises(DownloadTimeoutError):
        handler()._download(Request("https://example.com"))  # noqa: SLF001


def test_download_failed(monkeypatch):
    def fake_request(**kwargs):
        raise CurlConnectionError("connection reset")

    monkeypatch.setattr(downloadhandlers.requests, "request", fake_request)

    with pytest.raises(DownloadFailedError):
        handler()._download(Request("https://example.com"))  # noqa: SLF001
