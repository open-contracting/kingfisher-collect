from unittest.mock import Mock

import pytest
from scrapy import Request
from scrapy.exceptions import IgnoreRequest
from scrapy.http import Response

from kingfisher_scrapy import downloadermiddlewares
from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.downloadermiddlewares import CloudflareMiddleware
from tests import spider_with_crawler


class CloudflareSpider(BaseSpider):
    name = "test"
    cloudflare_protected = True


def middleware_for(spider_class=CloudflareSpider, **settings):
    spider = spider_with_crawler(spider_class, settings={"CF_CLEARANCE": "token", "CF_USER_AGENT": "UA", **settings})
    return CloudflareMiddleware(spider.crawler), spider


def test_process_request_cookie_add():
    middleware, _ = middleware_for()
    request = Request("https://opentender.eu/data/downloads/data-ie-ocds-json.zip")

    middleware.process_request(request)

    assert request.headers["Cookie"] == b"cf_clearance=token"


def test_process_request_cookie_append():
    middleware, _ = middleware_for()
    request = Request("https://opentender.eu/x.zip", headers={"Cookie": "session=1"})

    middleware.process_request(request)

    assert request.headers["Cookie"] == b"session=1; cf_clearance=token"


def test_process_request_cloudflare_unprotected():
    middleware, _ = middleware_for(spider_class=type("Plain", (BaseSpider,), {"name": "test"}))
    request = Request("https://example.com")

    middleware.process_request(request)

    assert b"Cookie" not in request.headers


@pytest.mark.parametrize("content_type", ["text/html", "text/html; charset=UTF-8"])
def test_process_response_challenge(monkeypatch, content_type):
    middleware, spider = middleware_for()
    spider.crawler.engine = Mock()
    monkeypatch.setattr(downloadermiddlewares, "deferred_from_coro", lambda *_: None)
    alerts = []

    def fake_alert(webhook_url, text):
        alerts.append((webhook_url, text))

    monkeypatch.setattr(downloadermiddlewares, "post_slack_alert", fake_alert)

    request = Request("https://opentender.eu/data/downloads/data-ie-ocds-json.zip")
    response = Response(
        request.url, status=200, headers={"Content-Type": content_type}, body=b"<html>", request=request
    )

    with pytest.raises(IgnoreRequest):
        middleware.process_response(request, response)

    spider.crawler.engine.close_spider_async.assert_called_once_with(reason="cf_clearance_stale")
    assert len(alerts) == 1
    assert request.url in alerts[0][1]


def test_process_response_no_challenge():
    middleware, _ = middleware_for()
    request = Request("https://opentender.eu/data/downloads/data-ie-ocds-json.zip")
    response = Response(request.url, status=200, headers={"Content-Type": "application/zip"}, body=b"PK\x03\x04data")

    assert middleware.process_response(request, response) is response


def test_process_response_cloudflare_unprotected():
    middleware, _ = middleware_for(spider_class=type("Plain", (BaseSpider,), {"name": "test"}))
    request = Request("https://example.com")
    response = Response(request.url, status=200, headers={"Content-Type": "text/html"}, body=b"Just a moment")

    assert middleware.process_response(request, response) is response
