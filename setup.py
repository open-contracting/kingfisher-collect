# This file is used by scrapyd-deploy.

from setuptools import find_packages, setup

setup(
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={
        'kingfisher_scrapy': ['schema/*.json'],
    },
    include_package_data=True,
    entry_points={
        'scrapy': [
            'settings = kingfisher_scrapy.settings',
        ],
    },
)
