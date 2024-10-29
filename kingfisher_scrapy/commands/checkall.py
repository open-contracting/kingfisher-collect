
import logging
import os.path
import re
import sys
from textwrap import dedent

import requests
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import NotSupported
from scrapy.utils.misc import walk_modules
from scrapy.utils.spider import iter_spider_classes

from kingfisher_scrapy.base_spiders import PeriodicSpider

logger = logging.getLogger(__name__)

word_boundary_re = re.compile(
    r"""
    (?<=[a-z])(?=[A-Z])
    |(?<=.)(?=[A-Z][a-z])
    |(?<=EcuadorSERCOP)
    |(?<=HondurasSEFIN)
    |(?<=MexicoINAI)
    |(?<=PakistanPPRA)
    |(?<=PeruOSCE)
    """,
    flags=re.VERBOSE
)

year_re = re.compile(r'20\d\d\.\Z')


class CheckAll(ScrapyCommand):
    def short_desc(self):
        return 'Check that spiders are documented and well-implemented'

    def run(self, args, opts):
        level = getattr(logging, self.settings['LOG_LEVEL'])

        try:
            response = requests.get('https://data.open-contracting.org/publications.json', timeout=10)
            response.raise_for_status()
            publications = response.json()
        except requests.RequestException:  # pre-commit.ci blocks network connections
            publications = {}

        publications = {publication['source_id']: publication for publication in publications}
        # Copy publications for *_releases/*_records pairs of spiders.
        for source_id in list(publications):
            if source_id.endswith('_releases'):
                publications[f'{source_id[:-9]}_records'] = publications[source_id]
            elif source_id.endswith('_records'):
                publications[f'{source_id[:-8]}_releases'] = publications[source_id]

        has_output = False
        for module in walk_modules('kingfisher_scrapy.spiders'):
            if not args or os.path.relpath(module.__file__) in args:
                source_id = module.__name__.rsplit('.', 1)[-1]
                for cls in iter_spider_classes(module):
                    checker = Checker(module, cls, publications.get(source_id, {}), level)
                    checker.check()
                    has_output |= checker.has_output

        if has_output:
            sys.exit(1)

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
        'publisher',
        'system',
        'sample',
        'portal',
    ]

    conditional_spider_arguments = {
        'available_publishers': 'publisher',
        'available_systems': 'system',
    }

    def __init__(self, module, cls, publication, level):
        self.module = module
        self.cls = cls
        self.publication = publication
        self.level = level

        #: Whether the check() call produced output.
        self.has_output = False

    def log(self, level, message, *args):
        if getattr(logging, level.upper()) >= self.level:
            self.has_output = True
        getattr(logger, level)(f'%s.%s: {message}', self.module.__name__, self.cls.__name__, *args)

    def check(self):
        class_name = self.cls.__name__
        docstring = self.cls.__doc__

        basename = os.path.splitext(os.path.basename(self.module.__file__))[0]
        expected_basename = re.sub(word_boundary_re, '_', class_name).lower()

        if basename != expected_basename:
            self.log('error', 'class %s and file %s (%s) do not match', class_name, basename, expected_basename)

        if self.cls.name != basename:
            self.log('error', 'spider name %s and file name %s do not match', self.cls.name, basename)

        if class_name.endswith(('Base', 'Digiwhist')):
            if docstring:
                self.log('error', 'unexpected docstring')
            return

        if not docstring:
            self.log('error', 'missing docstring')
            return

        # docutils doesn't provide a Document Object Model (DOM) for navigating nodes in reStructured Text, so we use
        # regular expressions instead.
        docstring = dedent(docstring)

        # Spider metadata

        terms = dict(re.findall(r'^(\S.+)\n  (.+)', docstring, re.MULTILINE))

        self.check_list(terms, self.known_terms, 'terms')

        if 'Domain' not in terms:
            self.log('error', 'missing term: "Domain"')

        retrieval_frequency = self.publication.get('retrieval_frequency')
        if retrieval_frequency == 'NEVER' and not year_re.search(terms.get('Caveats', '')):
            self.log('error', 'missing "Caveats" term for publication that has ended')
        elif retrieval_frequency and retrieval_frequency != 'NEVER' and year_re.search(terms.get('Caveats', '')):
            self.log('error', 'unexpected "Caveats" term for publication that has not ended')

        # Spider arguments

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
            # Ukraine requires a date, but only supports from_date.
            if self.cls.__name__ == 'Ukraine':
                expected_spider_arguments.remove('until_date')

        for spider_argument in expected_spider_arguments:
            if spider_argument not in spider_arguments:
                self.log('warning', 'missing "%s" spider argument documentation', spider_argument)

        for cls_attribute, spider_argument in self.conditional_spider_arguments.items():
            if hasattr(self.cls, cls_attribute) and spider_argument not in spider_arguments:
                self.log('warning', 'missing "%s" spider argument (%s is set)', spider_argument, cls_attribute)
            if not hasattr(self.cls, cls_attribute) and spider_argument in spider_arguments:
                self.log('warning', 'unexpected "%s" spider argument (%s is not set)', spider_argument, cls_attribute)

        def default_from_date(cls):
            return repr(getattr(cls, 'default_from_date', None))

        self.check_date_spider_argument('from_date', spider_arguments, default_from_date,
                                        'Download only data from this {period} onward ({format} format).')

        def default_until_date(cls):
            if hasattr(cls, 'default_until_date'):
                return f"'{cls.default_until_date}'"
            match cls.date_format:
                case 'datetime':
                    return 'now'
                case 'date':
                    return 'today'
                case 'year-month':
                    return 'the current month'
                case 'year':
                    return 'the current year'
                case _:
                    return None

        self.check_date_spider_argument('until_date', spider_arguments, default_until_date,
                                        'Download only data until this {period} ({format} format).')

    def check_list(self, items, known_items, name):
        items = list(items)

        for item in known_items:
            if items and items[0] == item:
                items.pop(0)

        unexpected = set(items) - set(known_items)
        if unexpected:
            self.log('error', 'unexpected %s: %s', name, ', '.join(unexpected))

        disordered = set(items) & set(known_items)
        if disordered:
            self.log('error', 'out-of-order %s: %s', name, ', '.join(disordered))

    def check_date_spider_argument(self, spider_argument, spider_arguments, default, format_string):
        if spider_argument in spider_arguments:
            # These classes are known to have more specific semantics.
            if self.cls.__name__ in {
                'ColombiaBulk', 'Kosovo', 'PortugalRecords', 'PortugalReleases', 'UgandaReleases', 'Ukraine'
            }:
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
                raise NotSupported(f'checkall: date_format "{self.cls.date_format}" not implemented')

            expected = format_string.format(period=period, format=format_, default=default(self.cls))
            if spider_arguments[spider_argument] != expected:
                self.log(level, '\n%r !=\n%r', spider_arguments[spider_argument], expected)
