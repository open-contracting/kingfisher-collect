import pytest

from kingfisher_scrapy.exceptions import MissingRequiredFieldError
from kingfisher_scrapy.items import File
from kingfisher_scrapy.pipelines import Validate


def test_process_item():
    pipeline = Validate()
    item = File({
        'file_name': '',
        'data': '',
        'data_type': '',
        'url': '',
    })

    assert pipeline.process_item(item, None) == item


def test_process_item_error():
    pipeline = Validate()
    item = File()

    with pytest.raises(MissingRequiredFieldError):
        pipeline.process_item(item, None)
