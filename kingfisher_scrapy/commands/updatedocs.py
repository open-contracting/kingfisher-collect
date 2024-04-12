import re
from itertools import groupby
from pathlib import Path
from textwrap import dedent

from scrapy.commands import ScrapyCommand
from scrapy.utils.misc import walk_modules
from scrapy.utils.spider import iter_spider_classes


class UpdateDocs(ScrapyCommand):
    def short_desc(self):
        return 'Update docs/spiders.rst'

    def run(self, args, opts):
        basedir = Path(__file__).resolve().parents[2]

        def _keyfunc(module):
            module_name = module.__name__.rsplit('.', 1)[-1]
            if module_name.startswith(('costa_rica', 'czech_republic', 'dominican_republic', 'north_macedonia',
                                       'south_africa', 'united_kingdom')):
                return '_'.join(module_name.split('_', 2)[:2])
            return module_name.split('_', 1)[0]

        with (basedir / 'docs' / 'spiders.rst').open() as f:
            lines = []
            for line in f:
                lines.append(line)
                if line.startswith('.. Do not edit past this line.'):
                    break

        with (basedir / 'docs' / 'spiders.rst').open('w') as f:
            for line in lines:
                f.write(line)

            for key, group in groupby(walk_modules('kingfisher_scrapy.spiders'), _keyfunc):
                if key == 'spiders':
                    continue

                classes = [(module, cls) for module in group for cls in iter_spider_classes(module)]
                if not classes:
                    continue

                f.write(f"\n{key.replace('_', ' ').title()}\n{'~' * len(key)}\n")

                for (module, cls) in classes:
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
