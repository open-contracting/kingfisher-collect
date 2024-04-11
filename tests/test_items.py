import pydantic
import pytest

from kingfisher_scrapy.items import File, FileError, FileItem

ITEM = {'file_name': 'test', 'url': 'http://test.com'}
FILE = {**ITEM | {'data_type': 'release_package', 'data': 'data'}}
FILE_ITEM = {**FILE | {'number': 1}}
FILE_ERROR = {**ITEM | {'errors': {'http_code': 500, 'detail': 'timeout'}}}


def check_required(klass, base, pop):
    data = base.copy()
    data.pop(pop)

    with pytest.raises(pydantic.ValidationError):
        klass(**data)


@pytest.mark.parametrize('klass,base', [(File, FILE), (FileItem, FILE_ITEM), (FileError, FILE_ERROR)])
def test_valid(klass, base):
    klass(**base)  # no exception raised


@pytest.mark.parametrize('pop', ['file_name', 'url', 'data_type'])
def test_file_required(pop):
    check_required(File, FILE, pop)


@pytest.mark.parametrize('pop', ['file_name', 'url', 'data_type', 'number'])
def test_file_item_required(pop):
    check_required(FileItem, FILE_ITEM, pop)


@pytest.mark.parametrize('pop', ['file_name', 'url', 'errors'])
def test_file_error_required(pop):
    check_required(FileError, FILE_ERROR, pop)


@pytest.mark.parametrize('klass,base', [(File, FILE), (FileItem, FILE_ITEM), (FileError, FILE_ERROR)])
def test_file_name(klass, base):
    with pytest.raises(pydantic.ValidationError):
        klass(**base | {'file_name': 'path/test'})


@pytest.mark.parametrize('invalid', ['://example.com', 'scheme://example.com', 'http://example'])
@pytest.mark.parametrize('klass,base', [(File, FILE), (FileItem, FILE_ITEM), (FileError, FILE_ERROR)])
def test_url(klass, base, invalid):
    with pytest.raises(pydantic.ValidationError):
        klass(**base | {'url': invalid})


@pytest.mark.parametrize('klass,base', [(File, FILE), (FileItem, FILE_ITEM)])
def test_data_type(klass, base):
    with pytest.raises(pydantic.ValidationError):
        klass(**base | {'data_type': 'invalid'})


@pytest.mark.parametrize('invalid', [-1, 0, '1'])
def test_number(invalid):
    with pytest.raises(pydantic.ValidationError):
        FileItem(**FILE_ITEM | {'number': invalid})


@pytest.mark.parametrize('invalid', [{'http_code': -1}, {'http_code': 0}, {'http_code': '1'}, {'detail': 'timeout'}])
def test_errors(invalid):
    with pytest.raises(pydantic.ValidationError):
        FileError(**FILE_ERROR | {'errors': invalid})
