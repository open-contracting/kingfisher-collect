import os
import glob
import inspect
import importlib

import ocdskingfisher.base


def gather_sources():
    sources = {}

    dir_path = os.path.dirname(os.path.realpath(__file__))
    sources_dir = os.path.join(dir_path, '..', 'ocdskingfisher', 'sources')
    for file in glob.glob(sources_dir + '/*.py'):
        module = importlib.import_module('ocdskingfisher.sources.' + file.split('/')[-1].split('.')[0])
        for item in dir(module):
            value = getattr(module, item)
            if inspect.isclass(value) \
                    and hasattr(value, 'source_id') \
                    and getattr(value, 'source_id') \
                    and issubclass(value, ocdskingfisher.base.Source) \
                    and value is not ocdskingfisher.base.Source:
                sources[getattr(value, 'source_id')] = value
    return sources
