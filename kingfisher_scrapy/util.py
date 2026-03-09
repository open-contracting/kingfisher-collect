import datetime
import itertools
from decimal import Decimal
from os.path import splitext
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

from ijson import ObjectBuilder, utils

BROWSER_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
)
MAX_DOWNLOAD_TIMEOUT = 1800  # 30min


def pluck_filename(opts):
    if opts.pluck_package_pointer:
        parts = ["pluck", "package", opts.pluck_package_pointer[1:].replace("/", "-")]
    else:  # opts.pluck_release_pointer
        parts = ["pluck", "release", opts.pluck_release_pointer[1:].replace("/", "-")]

    return f"{'-'.join(parts)}.csv"


def replace_path_separator(string):
    return string.replace("/", "_")


def components(start, stop=None):
    """
    Return a function that returns the selected non-empty path components, excluding the ``.json`` extension.

    >>> components(-1)('http://example.com/api/planning.json')
    'planning'

    >>> components(-2, -1)('http://example.com/api/planning/package.json')
    'planning'
    """

    def wrapper(url):
        value = "-".join(list(filter(None, urlsplit(url).path.split("/")))[start:stop])
        if value.endswith(".json"):
            return value[:-5]
        return value

    return wrapper


def parameters(*keys, parser=None):
    """
    Return a function that returns the selected query string parameters.

    >>> parameters('page')('http://example.com/api/packages.json?page=1')
    'page-1'

    >>> parameters('year', 'page')('http://example.com/api/packages.json?year=2000&page=1')
    'year-2000-page-1'
    """

    def wrapper(url):
        query = parse_qs(urlsplit(url).query)
        return "-".join(s for key in keys for value in query[key] for s in [key, parser(value) if parser else value])

    return wrapper


def join(*functions, extension=None):
    """
    Return a function that joins the given functions' outputs and sets the file extension, if provided.

    >>> join(components(-1), parameters('page'))('http://example.com/api/planning.json?page=1')
    'planning-page-1'
    """

    def wrapper(url):
        value = "-".join(function(url) for function in functions)
        if extension:
            return f"{value}.{extension}"
        return value

    return wrapper


def date_range_by_interval(start, stop, step):
    """
    Yield date ranges from the ``start`` date to the ``stop`` date, in intervals of ``step`` days, in reverse
    chronological order.
    """
    delta = datetime.timedelta(days=step)
    range_end = stop
    while range_end > start:
        range_start = max(start, range_end - delta)
        yield range_start, range_end
        range_end = range_start


# https://stackoverflow.com/questions/34898525/generate-list-of-months-between-interval-in-python
def date_range_by_month(start, stop):
    """
    Yield the first day of the month as a ``date`` from the ``start`` to the ``stop`` dates, in reverse chronological
    order.
    """

    def number_of_months(d):
        return 12 * d.year + d.month

    for months in reversed(range(number_of_months(start) - 1, number_of_months(stop))):
        year, month = divmod(months, 12)
        yield datetime.date(year, month + 1, 1)


def date_range_by_year(start, stop):
    """Return the year as an ``int`` from the ``start`` to the ``stop`` years, in reverse chronological order."""
    return reversed(range(start, stop + 1))


def get_parameter_value(url, key):
    """Return the first value of the query string parameter."""
    query = parse_qs(urlsplit(url).query)
    if key in query:
        return query[key][0]
    return None


def replace_parameters(url, **kwargs):
    """Return a URL after updating the query string parameters' values."""
    parsed = urlsplit(url)
    query = parse_qs(parsed.query)
    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = [value]
    return parsed._replace(query=urlencode(query, doseq=True)).geturl()


def append_path_components(url, path):
    """Return a URL after appending path components to its path."""
    parsed = urlsplit(url)
    return urljoin(parsed._replace(path=f"{parsed.path}/").geturl(), quote(path.lstrip("/")))


def add_query_string(method, params):
    """
    Return a function that yields the requests yielded by the wrapped method, after updating the query string
    parameter values in each request's URL.
    """

    def wrapper(*args, **kwargs):
        for request in method(*args, **kwargs):
            url = replace_parameters(request.url, **params)
            yield request.replace(url=url)

    return wrapper


def add_path_components(method, path):
    """
    Return a function that yields the requests yielded by the wrapped method, after appending path components
    to each request's URL.
    """

    def wrapper(*args, **kwargs):
        for request in method(*args, **kwargs):
            url = append_path_components(request.url, path)
            yield request.replace(url=url)

    return wrapper


@utils.coroutine
def items_basecoro(target, prefix, map_type=None, skip_key=None):
    """
    Replicate the same function from ``ijson/common.py``.

    A ``skip_key`` argument is added. If the ``skip_key`` is in the current path, the current event is skipped.
    Otherwise, the method is identical.
    """
    while True:
        current, event, value = yield
        if skip_key and skip_key in current:
            continue
        if current == prefix:
            if event in {"start_map", "start_array"}:
                builder = ObjectBuilder(map_type=map_type)
                end_event = event.replace("start", "end")
                while (current, event) != (prefix, end_event):
                    builder.event(event, value)
                    current, event, value = yield
                del builder.containers[:]
                target.send(builder.value)
            else:
                target.send(value)


def items(events, prefix, map_type=None, skip_key=None):
    """
    Replicate the same function from ``ijson/common.py``.

    A ``skip_key`` argument is added, which is passed as a keyword argument to
    :meth:`~kingfisher_scrapy.util.items_basecoro`. Otherwise, the method is identical.
    """
    return utils.coros2gen(events, (items_basecoro, (prefix,), {"map_type": map_type, "skip_key": skip_key}))


def default(obj):
    """Convert decimals to floats and iterables to lists."""
    if isinstance(obj, Decimal):
        return float(obj)
    return list(iter(obj))


class TranscodeFile:
    def __init__(self, file, encoding):
        self.file = file
        self.encoding = encoding

    def read(self, buf_size):
        """Re-encodes bytes read from the file to UTF-8."""
        data = self.file.read(buf_size)
        return transcode_bytes(data, self.encoding)


def transcode_bytes(data, encoding):
    """Re-encodes bytes to UTF-8."""
    return data.decode(encoding).encode()


def transcode(spider, function, data, *args, **kwargs):
    if spider.encoding != "utf-8":
        if hasattr(data, "read"):
            data = TranscodeFile(data, spider.encoding)
        else:
            data = transcode_bytes(data, spider.encoding)

    return function(data, *args, **kwargs)


# See `grouper` recipe: https://docs.python.org/3/library/itertools.html#recipes
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def get_file_name_and_extension(filename):
    """
    Given a ``filename``, return its name and extension in two separate strings.

    >>> get_file_name_and_extension('test.json')
    ('test', 'json')
    """
    name, extension = splitext(filename)
    extension = extension[1:].lower()
    return name, extension
