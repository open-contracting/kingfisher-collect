from scrapy.settings import Settings

from kingfisher_scrapy.extensions.sentry_logging import before_send, get_secrets

WEBHOOK_PATH = "/services/T00000000/B00000000/webhooksecret"


def test_get_secrets():
    settings = Settings(
        {
            "CF_CLEARANCE": "cookie",
            "KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN": "token",
            "RABBIT_URL": "amqp://user:password@localhost:5672?connection_attempts=3",
            "SLACK_WEBHOOK_URL": f"https://hooks.slack.com{WEBHOOK_PATH}",
        }
    )

    assert get_secrets(settings) == ["cookie", "token", "webhooksecret", "password"]


def test_get_secrets_unset():
    assert get_secrets(Settings()) == []


def test_before_send():
    event = {
        "exception": {
            "values": [
                {
                    "value": f"HTTPSConnectionPool(host='hooks.slack.com', port=443): Max retries exceeded with url: "
                    f"{WEBHOOK_PATH} (Caused by ProxyError('Unable to connect to proxy'))",
                    "stacktrace": {"frames": [{"vars": {"webhook_url": f"'https://hooks.slack.com{WEBHOOK_PATH}'"}}]},
                }
            ]
        },
        "extra": {"sys.argv": ["runner.py", "spider", "-s", "CF_CLEARANCE=cookie", "-s", "CF_USER_AGENT=Mozilla/5.0"]},
    }

    assert before_send(event, {}, secrets=["webhooksecret", "cookie"]) == {
        "exception": {
            "values": [
                {
                    "value": "HTTPSConnectionPool(host='hooks.slack.com', port=443): Max retries exceeded with url: "
                    "/services/T00000000/B00000000/[Filtered] (Caused by ProxyError('Unable to connect to proxy'))",
                    "stacktrace": {
                        "frames": [
                            {
                                "vars": {
                                    "webhook_url": "'https://hooks.slack.com/services/T00000000/B00000000/[Filtered]'"
                                }
                            }
                        ]
                    },
                }
            ]
        },
        "extra": {
            "sys.argv": ["runner.py", "spider", "-s", "CF_CLEARANCE=[Filtered]", "-s", "CF_USER_AGENT=Mozilla/5.0"]
        },
    }
