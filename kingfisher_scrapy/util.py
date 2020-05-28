import itertools
import json
from decimal import Decimal
from functools import wraps

from ijson import ObjectBuilder, utils


def handle_error(decorated):
    """
    A decorator for spider parse methods.

    Yields a :class:`~kingfisher_scrapy.items.FileError` for non-2xx HTTP status codes.
    """
    @wraps(decorated)
    def wrapper(self, response):
        # All 2xx codes are successful.
        # https://tools.ietf.org/html/rfc7231#section-6.3
        if self.is_http_success(response):
            yield from decorated(self, response)
        else:
            yield self.build_file_error_from_response(response)
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
