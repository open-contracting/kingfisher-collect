import json
import os
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.items import File
from tests import FILE_LENGTH, path, response_fixture, spider_with_crawler


def test_parse():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = "release_package"

    io = BytesIO()
    with ZipFile(io, "w", compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr("test.json", "{}")

    response = response_fixture(body=io.getvalue(), meta={"file_name": "test.zip"})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item.__dict__) == FILE_LENGTH
    assert item.file_name == "test-test.json"
    assert item.url == "http://example.com"
    assert item.data_type == "release_package"
    assert item.data is not None
    assert "package" not in item.data

    with pytest.raises(StopIteration):
        next(generator)


@pytest.mark.parametrize(("sample", "len_items", "file_name"), [(None, 20, "test"), (5, 5, "test")])
def test_parse_line_delimited(sample, len_items, file_name):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = "release_package"
    spider.line_delimited = True

    content = ['{"key": %s}\n' % i for i in range(1, 21)]  # noqa: UP031

    io = BytesIO()
    with ZipFile(io, "w", compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr("test.json", "".join(content))

    response = response_fixture(body=io.getvalue(), meta={"file_name": f"{file_name}.zip"})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item.__dict__) == FILE_LENGTH
    assert item.file_name == f"{file_name}-test.json"
    assert item.url == "http://example.com"
    assert item.data_type == "release_package"
    assert item.data is not None
    assert "package" not in item.data

    with pytest.raises(StopIteration):
        next(generator)


@pytest.mark.parametrize(
    ("sample", "len_items", "len_releases", "file_name"), [(None, 2, 100, "test"), (5, 1, 5, "test")]
)
def test_parse_release_package(sample, len_items, len_releases, file_name):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = "release_package"
    spider.resize_package = True

    package = {"releases": []}
    for _ in range(200):
        package["releases"].append({"key": "value"})

    io = BytesIO()
    with ZipFile(io, "w", compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr("test.json", json.dumps(package))

    response = response_fixture(body=io.getvalue(), meta={"file_name": f"{file_name}.zip"})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item.__dict__) == FILE_LENGTH
    assert item.file_name == f"{file_name}-test.json"
    assert item.url == "http://example.com"
    assert item.data_type == "release_package"
    assert item.data["package"] is not None
    assert item.data["data"] is not None

    with pytest.raises(StopIteration):
        next(generator)


def test_parse_zip_empty_dir():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = "release_package"

    io = BytesIO()
    with ZipFile(io, "w", compression=ZIP_DEFLATED) as zipfile:
        empty_folder = ZipInfo(os.path.join("test", "test", "/"))
        zipfile.writestr(empty_folder, "")
    response = response_fixture(body=io.getvalue(), meta={"file_name": "test.zip"})
    generator = spider.parse(response)

    with pytest.raises(StopIteration):
        next(generator)


def test_parse_rar_file():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = "release_package"

    with open(path("test.rar"), "rb") as f:
        io = BytesIO(f.read())
    response = response_fixture(body=io.getvalue(), meta={"file_name": "test.rar"})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item.__dict__) == FILE_LENGTH
    assert item.file_name == "test-test.json"
    assert item.url == "http://example.com"
    assert item.data_type == "release_package"
    assert item.data is not None
    assert "package" not in item.data

    with pytest.raises(StopIteration):
        next(generator)


def test_yield_non_archive_file():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = "release_package"
    spider.yield_non_archive_file = True

    response = response_fixture(body=b'{"ocid": "abc"}', meta={"file_name": "test.json"})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert item.file_name == "test.json"
    assert item.url == "http://example.com"
    assert item.data_type == "release_package"
    assert item.data is not None

    with pytest.raises(StopIteration):
        next(generator)


@pytest.mark.parametrize(("include", "exclude"), [("", "skip"), ("test", "")])
def test_filter_file_names(include, exclude):
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = "release_package"
    spider.file_name_must_contain = include
    spider.file_name_must_not_contain = exclude

    io = BytesIO()
    with ZipFile(io, "w", compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr("test.json", "{}")
        zipfile.writestr("skip.json", "{}")
        zipfile.writestr("__MACOSX/garbage.json", "")

    response = response_fixture(body=io.getvalue(), meta={"file_name": "test.zip"})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert item.file_name == "test-test.json"

    with pytest.raises(StopIteration):
        next(generator)
