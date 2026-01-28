import pytest
from scrapy.cmdline import execute


def test_command(caplog):
    with pytest.raises(SystemExit):
        execute(["scrapy", "updatedocs"])

    assert len(caplog.records) > 0
