import itertools
import json
from decimal import Decimal

from ijson import ObjectBuilder, utils


@utils.coroutine
def items_basecoro(target, prefix, map_type=None, array_name=None):
    """
    This is copied from ``ijson/common.py``. An ``array_name`` argument is added. If the ``array_name`` is in the
    current path, the current event is skipped. Otherwise, the method is identical.
    """
    while True:
        current, event, value = (yield)
        if array_name and array_name in current:
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


def items(events, prefix, map_type=None, array_name=None):
    """
    This is copied from ``ijson/common.py``. An ``array_name`` argument is added, which is passed as a keyword argument
    to :meth:`~kingfisher_scrapy.util.items_basecoro`. Otherwise, the method is identical.
    """
    return utils.coros2gen(events,
        (items_basecoro, (prefix,), {'map_type': map_type, 'array_name': array_name})  # noqa: E128
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
