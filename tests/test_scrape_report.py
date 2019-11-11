import os
import pytest
from kingfisher_scrapy.scrape_report import ScrapeReport


@pytest.mark.parametrize(('in_file', 'out_file'), [
    ('canada_buyandsell.txt', 'canada_buyandsell_results.txt'),
])
def test_scrape_report(in_file, out_file):
    scrape_stats = ScrapeReport(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', in_file))
    scrape_stats.go()
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', out_file)) as fp:
        expected = fp.readlines()
    assert ''.join(expected).strip() == scrape_stats.stats.strip()
