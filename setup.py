from setuptools import setup

setup(
    name='ocdskingfisher-scrape',
    version='0.0.1',
    author='Open Contracting Partnership, Open Data Services, Iniciativa Latinoamericana para los Datos Abiertos',
    author_email='data@open-contracting.org',
    url='https://open-contracting.org',
    license='BSD',
    packages=[
        'kingfisher_scrapy',
        'kingfisher_scrapy.spiders',
    ],
    entry_points={'scrapy': ['settings = kingfisher_scrapy.settings']},
)
