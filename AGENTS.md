Before writing or reviewing a spider, read the "Write a spider" section of `docs/contributing/index.rst`, especially "Write the spider". Before writing a feature, read its "Write a feature" section.

To check a spider:

- Run it, setting the `sample` argument because some sources are large (`scrapy crawl spider_name -a sample=10`), and check the log for errors, per `docs/logs.rst`.
- Run `scrapy updatedocs` and `scrapy checkall --loglevel=WARNING`.
- Run `pytest`. Pre-commit runs Ruff and scrapy-lint.
