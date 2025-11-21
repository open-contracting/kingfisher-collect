# See scrapy/conftest.py
from scrapy.utils.reactor import set_asyncio_event_loop_policy


def pytest_configure(config):
    if config.getoption("--reactor") == "asyncio":
        set_asyncio_event_loop_policy()
