import pytest
from jsonschema import ValidationError

from kingfisher_scrapy.items import File
from kingfisher_scrapy.pipelines import Validate


def test_process_item():
    pipeline = Validate()
    item = File({
        'file_name': 'test',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
    })

    assert pipeline.process_item(item, None) == item


def test_process_item_error():
    pipeline = Validate()
    item = File()

    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)
