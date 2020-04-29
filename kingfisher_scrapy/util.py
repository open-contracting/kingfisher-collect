import itertools
import json
from decimal import Decimal

from ijson import utils, ObjectBuilder


@utils.coroutine
def items_basecoro(target, prefix, map_type=None, array_name=None):
    """
    An couroutine dispatching native Python objects constructed from the events
    under a given prefix.
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
    """Like ijson.items, but takes events generated via ijson.parse instead of
    a file"""
    return utils.coros2gen(events, (items_basecoro, (prefix, ), {'map_type': map_type, 'array_name': array_name}))


def default(obj):
    """
    From ocdskit, returns the data as JSON.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    try:
        iter(obj)
    except TypeError:
        pass
    return json.JSONEncoder().default(obj)


# See `grouper` recipe: https://docs.python.org/3.8/library/itertools.html#recipes
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)
