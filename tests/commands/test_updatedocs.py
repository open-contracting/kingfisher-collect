import pytest
from scrapy.cmdline import execute


# tests/extensions/test_kingfisher_process_api.py fails if execute() is already called.
@pytest.mark.order(-1)
def test_command(caplog):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'updatedocs'])

    assert len(caplog.records) > 0
