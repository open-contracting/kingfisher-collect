import logging
import re
from textwrap import dedent

from scrapy.commands import ScrapyCommand
from scrapy.utils.misc import walk_modules
from scrapy.utils.spider import iter_spider_classes

from kingfisher_scrapy.base_spider import PeriodicSpider

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
    # https://github.com/open-contracting/kingfisher-archive/blob/main/ocdskingfisherarchive/scrapy_log_file.py
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

    conditional_spider_arguments = {
        'available_publishers': 'publisher',
        'available_systems': 'system',
    }

    def __init__(self, module, cls):
        self.cls = cls
        self.module = module

    def log(self, level, message):
        getattr(logger, level)('%s.%s: %s', self.module.__name__, self.cls.__name__, message)

    def check(self):
        class_name = self.cls.__name__
        docstring = self.cls.__doc__

        if class_name.endswith('Base') or class_name.startswith('Digiwhist') or class_name in ('Fail',):
            if docstring:
                self.log('error', 'unexpected docstring')
            return

        if not docstring:
            self.log('error', 'missing docstring')
            return

        # docutils doesn't provide a Document Object Model (DOM) for navigating nodes in reStructured Text, so we use
        # regular expressions instead.
        docstring = dedent(docstring)

        # Spider metadata.
        terms = re.findall(r'^(\S.+)\n  ', docstring, re.MULTILINE)

        self.check_list(terms, self.known_terms, 'terms')

        if 'Domain' not in terms:
            self.log('error', 'missing term: "Domain"')

        # Spider arguments.
        section = re.search(r'^Spider arguments\n(.+?)(?:^\S|\Z)', docstring, re.MULTILINE | re.DOTALL)
        if section:
            matches = re.findall(r'^(\S.+)((?:\n  .+)+)', dedent(section[1]), re.MULTILINE)
            spider_arguments = {k: v.strip() for k, v in matches}
        else:
            spider_arguments = {}

        self.check_list(spider_arguments, self.known_spider_arguments, 'spider arguments')

        if 'sample' in spider_arguments:
            self.log('error', 'unexpected "sample" spider argument (document it globally)')

        expected_spider_arguments = set()
        if PeriodicSpider in self.cls.__bases__:
            expected_spider_arguments.update({'from_date', 'until_date'})
        elif self.cls.date_required:
            expected_spider_arguments.update({'from_date', 'until_date'})

        for spider_argument in expected_spider_arguments:
            if spider_argument not in spider_arguments:
                self.log('warning', f'missing "{spider_argument}" spider argument documentation')

        for class_attribute, spider_argument in self.conditional_spider_arguments.items():
            if hasattr(self.cls, class_attribute) and spider_argument not in spider_arguments:
                self.log('warning', f'missing "{spider_argument}" spider argument ({class_attribute} is set)')
            if not hasattr(self.cls, class_attribute) and spider_argument in spider_arguments:
                self.log('warning', f'unexpected "{spider_argument}" spider argument ({class_attribute} is not set)')

        self.check_date_spider_argument('from_date', spider_arguments, lambda cls: repr(cls.default_from_date),
                                        'Download only data from this {period} onward ({format} format).')

        def default(cls):
            if hasattr(cls, 'default_until_date'):
                return f"'{cls.default_until_date}'"
            if cls.date_format == 'datetime':
                return 'now'
            elif cls.date_format == 'date':
                return 'today'
            elif cls.date_format == 'year-month':
                return 'the current month'
            elif cls.date_format == 'year':
                return 'the current year'

        self.check_date_spider_argument('until_date', spider_arguments, default,
                                        'Download only data until this {period} ({format} format).')

    def check_list(self, items, known_items, name):
        items = list(items)

        for i, item in enumerate(known_items):
            if items and items[0] == known_items[i]:
                items.pop(0)

        unexpected = set(items) - set(known_items)
        if unexpected:
            self.log('error', f"unexpected {name}: {', '.join(unexpected)}")

        disordered = set(items) & set(known_items)
        if disordered:
            self.log('error', f"out-of-order {name}: {', '.join(disordered)}")

    def check_date_spider_argument(self, spider_argument, spider_arguments, default, format_string):
        if spider_argument in spider_arguments:
            # These classes are known to have more specific semantics.
            if self.cls.__name__ in ('Australia', 'ColombiaBulk', 'PortugalRecords', 'PortugalReleases',
                                     'ScotlandPublicContracts'):
                level = 'info'
            else:
                level = 'warning'

            if self.cls.date_required:
                format_string += " Defaults to {default}."
            elif spider_argument == 'from_date' and 'until_date' in spider_arguments:
                format_string += "\n  If ``until_date`` is provided, defaults to {default}."
            elif spider_argument == 'until_date' and 'from_date' in spider_arguments:
                format_string += "\n  If ``from_date`` is provided, defaults to {default}."

            if self.cls.date_format == 'datetime':
                period = 'time'
                format_ = 'YYYY-MM-DDThh:mm:ss'
            elif self.cls.date_format == 'date':
                period = 'date'
                format_ = 'YYYY-MM-DD'
            elif self.cls.date_format == 'year-month':
                period = 'month'
                format_ = 'YYYY-MM'
            elif self.cls.date_format == 'year':
                period = 'year'
                format_ = 'YYYY'
            else:
                raise NotImplementedError(f'checkall: date_format "{self.cls.date_format}" not implemented')

            expected = format_string.format(period=period, format=format_, default=default(self.cls))
            if 'None' in expected:
                self.log(level, f"\nA default_{spider_argument} must be set")
            elif spider_arguments[spider_argument] != expected:
                self.log(level, f"\n{spider_arguments[spider_argument]!r} !=\n{expected!r}")
