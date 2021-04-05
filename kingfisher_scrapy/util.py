import itertools
import json
from decimal import Decimal
from functools import wraps
from os.path import splitext
from urllib.parse import parse_qs, urlencode, urlsplit

from ijson import ObjectBuilder, utils


def _pluck_filename(opts):
    if opts.package_pointer:
        parts = ['pluck', 'package', opts.package_pointer[1:].replace('/', '-')]
    else:
        parts = ['pluck', 'release', opts.release_pointer[1:].replace('/', '-')]

    return f"{'-'.join(parts)}.csv"


def components(start, stop=None):
    """
    Returns a function that returns the selected non-empty path components, excluding the ``.json`` extension.

    >>> components(-1)('http://example.com/api/planning.json')
    'planning'

    >>> components(-2, -1)('http://example.com/api/planning/package.json')
    'planning'
    """
    def wrapper(url):
        value = '-'.join(list(filter(None, urlsplit(url).path.split('/')))[start:stop])
        if value.endswith('.json'):
            return value[:-5]
        return value
    return wrapper


def parameters(*keys):
    """
    Returns a function that returns the selected query string parameters.

    >>> parameters('page')('http://example.com/api/packages.json?page=1')
    'page-1'

    >>> parameters('year', 'page')('http://example.com/api/packages.json?year=2000&page=1')
    'year-2000-page-1'
    """
    def wrapper(url):
        query = parse_qs(urlsplit(url).query)
        return '-'.join(s for key in keys for value in query[key] for s in [key, value])
    return wrapper


def join(*functions, extension=None):
    """
    Returns a function that joins the given functions' outputs.

    >>> join(components(-1), parameters('page'))('http://example.com/api/planning.json?page=1')
    'planning-page-1'
    """
    def wrapper(url):
        value = '-'.join(function(url) for function in functions)
        if extension:
            return f'{value}.{extension}'
        return value
    return wrapper


def handle_http_error(decorated):
    """
    A decorator for spider parse methods.

    Yields a :class:`~kingfisher_scrapy.items.FileError` using
    :meth:`~kingfisher_scrapy.base_spider.BaseSpider.build_file_error_from_response`
    for unsuccessful HTTP status codes, determined using
    :meth:`~kingfisher_scrapy.base_spider.BaseSpider.is_http_success`.
    """
    @wraps(decorated)
    def wrapper(self, response, **kwargs):
        if self.is_http_success(response):
            yield from decorated(self, response, **kwargs)
        else:
            yield self.build_file_error_from_response(response)
    return wrapper


# https://stackoverflow.com/questions/34898525/generate-list-of-months-between-interval-in-python
def date_range_by_month(start, stop):
    """
    Yields the first day of the month as a ``date`` from the ``start`` to the ``stop`` dates, in reverse chronological
    order.
    """
    def number_of_months(d):
        return 12 * d.year + d.month

    for months in reversed(range(number_of_months(start) - 1, number_of_months(stop))):
        year, month = divmod(months, 12)
        yield date(year, month + 1, 1)


def date_range_by_year(start, stop):
    """
    Returns the year as an ``int`` from the ``start`` to the ``stop`` years, in reverse chronological order.
    """
    return reversed(range(start, stop + 1))


def get_parameter_value(url, key):
    """
    Returns the first value of the query string parameter.
    """
    query = parse_qs(urlsplit(url).query)
    if key in query:
        return query[key][0]


def replace_parameters(url, **kwargs):
    """
    Returns a URL after updating the query string parameters' values.
    """
    parsed = urlsplit(url)
    query = parse_qs(parsed.query)
    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = [value]
    return parsed._replace(query=urlencode(query, doseq=True)).geturl()


def add_query_string(method, params):
    """
    Returns a function that yields the requests yielded by the wrapped method, after updating their query string
    parameters' values.
    """
    def wrapper(*args, **kwargs):
        for request in method(*args, **kwargs):
            url = replace_parameters(request.url, **params)
            yield request.replace(url=url)
    return wrapper


@utils.coroutine
def items_basecoro(target, prefix, map_type=None, skip_key=None):
    """
    This is copied from ``ijson/common.py``. A ``skip_key`` argument is added. If the ``skip_key`` is in the current
    path, the current event is skipped. Otherwise, the method is identical.
    """
    while True:
        current, event, value = (yield)
        if skip_key and skip_key in current:
            continue
        if current == prefix:
            if event in ('start_map', 'start_array'):
                builder = ObjectBuilder(map_type=map_type)
                end_event = event.replace('start', 'end')
                while (current, event) != (prefix, end_event):
                    builder.event(event, value)
                    current, event, value = (yield)
                del builder.containers[:]
                target.send(builder.value)
            else:
                target.send(value)


def items(events, prefix, map_type=None, skip_key=None):
    """
    This is copied from ``ijson/common.py``. A ``skip_key`` argument is added, which is passed as a keyword argument to
    :meth:`~kingfisher_scrapy.util.items_basecoro`. Otherwise, the method is identical.
    """
    return utils.coros2gen(events,
        (items_basecoro, (prefix,), {'map_type': map_type, 'skip_key': skip_key})  # noqa: E128
    )


def default(obj):
    """
    Dumps JSON to a string, and returns it.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    try:
        iterable = iter(obj)
    except TypeError:
        pass
    else:
        return list(iterable)
    return json.JSONEncoder().default(obj)


# See `grouper` recipe: https://docs.python.org/3.8/library/itertools.html#recipes
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def get_file_name_and_extension(filename):
    """
    Given a ``filename`` returns its name and extension in two separate strings
    >>> get_file_name_and_extension('test.json')
    'test', 'json'
    """
    name, extension = splitext(filename)
    extension = extension[1:].lower()
    return name, extension
