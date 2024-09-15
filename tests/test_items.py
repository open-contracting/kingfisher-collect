import pydantic
import pytest

from kingfisher_scrapy.items import File, FileError, FileItem

ITEM = {'file_name': 'test', 'url': 'http://test.com'}
FILE = {**ITEM | {'data_type': 'release_package', 'data': b'{}'}}
FILE_ITEM = {**FILE | {'number': 1}}
FILE_ERROR = {**ITEM | {'errors': {'http_code': 500, 'detail': 'timeout'}}}


def check_required(cls, base, pop):
    data = base.copy()
    data.pop(pop)

    with pytest.raises(pydantic.ValidationError):
        cls(**data)


@pytest.mark.parametrize(('cls', 'base'), [(File, FILE), (FileItem, FILE_ITEM), (FileError, FILE_ERROR)])
def test_valid(cls, base):
    cls(**base)  # no exception raised


@pytest.mark.parametrize('pop', ['file_name', 'url', 'data_type'])
def test_file_required(pop):
    check_required(File, FILE, pop)


@pytest.mark.parametrize('pop', ['file_name', 'url', 'data_type', 'number'])
def test_file_item_required(pop):
    check_required(FileItem, FILE_ITEM, pop)


@pytest.mark.parametrize('pop', ['file_name', 'url', 'errors'])
def test_file_error_required(pop):
    check_required(FileError, FILE_ERROR, pop)


@pytest.mark.parametrize('invalid', ['path/test', 'path\\test'])
@pytest.mark.parametrize(('cls', 'base'), [(File, FILE), (FileItem, FILE_ITEM), (FileError, FILE_ERROR)])
def test_file_name(cls, base, invalid):
    with pytest.raises(pydantic.ValidationError):
        cls(**base | {'file_name': invalid})


@pytest.mark.parametrize('invalid', ['://example.com', 'scheme://example.com', 'http://example'])
@pytest.mark.parametrize(('cls', 'base'), [(File, FILE), (FileItem, FILE_ITEM), (FileError, FILE_ERROR)])
def test_url(cls, base, invalid):
    with pytest.raises(pydantic.ValidationError):
        cls(**base | {'url': invalid})


@pytest.mark.parametrize(('cls', 'base'), [(File, FILE), (FileItem, FILE_ITEM)])
def test_data_type(cls, base):
    with pytest.raises(pydantic.ValidationError):
        cls(**base | {'data_type': 'invalid'})


@pytest.mark.parametrize('invalid', [
    None, True, 1, 1.0, 'data', [{'ocid': 'x'}], ({'ocid': 'x'},), {('ocid', 'x')}, frozenset((('ocid', 'x'),))
])
@pytest.mark.parametrize(('cls', 'base'), [(File, FILE), (FileItem, FILE_ITEM)])
def test_data(cls, base, invalid):
    with pytest.raises(pydantic.ValidationError):
        cls(**base | {'data': invalid})


@pytest.mark.parametrize('invalid', [b'', {}])
@pytest.mark.parametrize(('cls', 'base'), [(File, FILE), (FileItem, FILE_ITEM)])
def test_data_length(cls, base, invalid):
    with pytest.raises(pydantic.ValidationError):
        cls(**base | {'data': invalid})


@pytest.mark.parametrize('invalid', [-1, 0, '1'])
def test_number(invalid):
    with pytest.raises(pydantic.ValidationError):
        FileItem(**FILE_ITEM | {'number': invalid})


@pytest.mark.parametrize('invalid', [
    {'http_code': 99},
    {'http_code': 600},
    {'http_code': '200'},
    {'detail': 'timeout'},
])
def test_errors(invalid):
    with pytest.raises(pydantic.ValidationError):
        FileError(**FILE_ERROR | {'errors': invalid})
