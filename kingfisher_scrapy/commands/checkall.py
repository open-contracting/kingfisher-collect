import logging
import re
from textwrap import dedent

from scrapy.commands import ScrapyCommand
from scrapy.utils.misc import walk_modules
from scrapy.utils.spider import iter_spider_classes

logger = logging.getLogger(__name__)


class CheckAll(ScrapyCommand):
    def short_desc(self):
        return 'Checks that spiders are documented and well-implemented'

    def run(self, args, opts):
        for module in walk_modules('kingfisher_scrapy.spiders'):
            for cls in iter_spider_classes(module):
                Checker(module, cls).check()


class Checker:
    # Add more terms as needed.
    known_terms = [
        'Domain',
        'Caveats',
        'Spider arguments',
        'Environment variables',
        'API documentation',
        'Bulk download documentation',
        'Swagger API documentation',
        'API endpoints',
    ]

    ########
    # NOTE #
    ########
    #
    # If you need to change this list, remember to update `ScrapyLogFile.is_complete()` in:
    # https://github.com/open-contracting/kingfisher-archive/blob/master/ocdskingfisherarchive/scrapy_log_file.py
    #
    # Add more spider arguments as needed.
    known_spider_arguments = [
        'from_date',
        'until_date',
        'year',
        'start_page',
        'publisher',
        'system',
        'sample',
    ]

    # Add more expected arguments as needed.
    expected_spider_arguments = [
        'from_date',
        'until_date',
    ]

    def __init__(self, module, cls):
        self.module_name = module.__name__
        self.class_name = cls.__name__
        self.docstring = cls.__doc__
        self.instance = cls.data_type

    def warn(self, message):
        print('')
        # logger.warning('%s.%s: %s', self.module_name, self.class_name, message)

    def error(self, message):
        print('')
        # logger.error('%s.%s: %s', self.module_name, self.class_name, message)

    def check_list(self, items, known_items, name):
        for i, item in enumerate(known_items):
            if items and items[0] == known_items[i]:
                items.pop(0)

        unexpected = set(items) - set(known_items)
        if unexpected:
            self.error(f"unexpected {name}: {', '.join(unexpected)}")

        disordered = set(items) & set(known_items)
        if disordered:
            self.error(f"out-of-order {name}: {', '.join(disordered)}")

    def check(self):

        if 'package' not in self.instance:
            print(self.class_name, self.instance)
        if self.class_name.endswith('Base') or self.class_name.startswith('Digiwhist') or self.class_name in ('Fail',):
            if self.docstring:
                self.error('unexpected docstring')
            return

        if not self.docstring:
            self.error('missing docstring')
            return

        # docutils doesn't provide a Document Object Model (DOM) for navigating nodes in reStructured Text, so we use
        # regular expressions instead.
        docstring = dedent(self.docstring)

        terms = re.findall(r'^(\S.+)\n  ', docstring, re.MULTILINE)
        if 'Domain' not in terms:
            self.error('missing term: "Domain"')
        self.check_list(terms, self.known_terms, 'terms')

        section = re.search(r'^Spider arguments\n(.+?)(?:^\S|\Z)', docstring, re.MULTILINE | re.DOTALL)
        if section:
            spider_arguments = re.findall(r'^(\S.+)\n  ', dedent(section[1]), re.MULTILINE)
            if 'sample' in spider_arguments:
                self.error('unexpected "sample" spider argument (document it globally)')
            for spider_argument in self.expected_spider_arguments:
                if spider_argument not in spider_arguments:
                    self.warn(f'missing "{spider_argument}" spider argument')
            self.check_list(spider_arguments, self.known_spider_arguments, 'spider arguments')
