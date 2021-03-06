from setuptools import setup

# This project is not intended to be released or used as a Python package. This file only exists for scrapyd-client.
# https://github.com/scrapy/scrapyd-client/blob/v1.1.0/README.rst

setup(
    packages=[
        'kingfisher_scrapy',
        'kingfisher_scrapy.spiders',
    ],
    package_data={
        'kingfisher_scrapy': ['item_schema/*.json'],
    },
    include_package_data=True,
    entry_points={
        'scrapy': [
            'settings = kingfisher_scrapy.settings',
        ],
    },
)
