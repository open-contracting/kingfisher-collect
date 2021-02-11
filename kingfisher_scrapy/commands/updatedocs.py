import os
import re
from itertools import groupby
from textwrap import dedent

from scrapy.commands import ScrapyCommand
from scrapy.utils.misc import walk_modules
from scrapy.utils.spider import iter_spider_classes


class UpdateDocs(ScrapyCommand):
    def short_desc(self):
        return 'Update docs/spiders.rst'

    def run(self, args, opts):
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        def _keyfunc(module):
            module_name = module.__name__.rsplit('.', 1)[-1]
            if module_name.startswith(('costa_rica', 'dominican_republic')):
                return '_'.join(module_name.split('_', 2)[:2])
            return module_name.split('_', 1)[0]

        with open(os.path.join(basedir, 'docs', 'spiders.rst')) as f:
            lines = []
            for line in f:
                lines.append(line)
                if line.startswith('.. Do not edit past this line.'):
                    break

        with open(os.path.join(basedir, 'docs', 'spiders.rst'), 'w') as f:
            for line in lines:
                f.write(line)

            for key, group in groupby(walk_modules('kingfisher_scrapy.spiders'), _keyfunc):
                if key in ('spiders', 'fail'):
                    continue

                f.write(f"\n{key.replace('_', ' ').title()}\n{'-' * len(key)}\n")

                for module in group:
                    for cls in iter_spider_classes(module):
                        f.write(f'\n.. autoclass:: {module.__name__}.{cls.__name__}\n   :no-members:\n')

                        infix = ''
                        if cls.__doc__:
                            section = re.search(r'^Environment variables\n(.+?)(?:^\S|\Z)', dedent(cls.__doc__),
                                                re.MULTILINE | re.DOTALL)
                            if section:
                                environment_variables = re.findall(r'^(\S.+)\n  ', dedent(section[1]), re.MULTILINE)
                                infix = f"env {' '.join([f'{variable}=...' for variable in environment_variables])} "

                        f.write('\n.. code-block:: bash\n')
                        f.write(f"\n   {infix}scrapy crawl {module.__name__.rsplit('.')[-1]}\n")
