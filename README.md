# OCDS Scrapy Scrapers

This repo contains scrapers for OCDS data from various publishers, using the [Scrapy](https://scrapy.org/) crawler framework. 

Initially sources are based on those in [OCDS Kingfisher](https://github.com/open-contracting/kingfisher).

## Install
```
 pip install -r requirements.txt 
```

## Configuration

### File storage

If you want to change where downloaded JSON is stored on disc, edit the `FILES_STORE` variable in `settings.py`.

### Kingfisher process

The scrapers post their results to an instance of [kingfisher-process](https://github.com/open-contracting/kingfisher-process), where things like validation, normalisation, and storage in a database can take place. See [kingfisher-process](https://github.com/open-contracting/kingfisher-process) for specifics, as well as how to install your own `kingfisher-process` instance (and note that this is a work in progress).

To configure the scrapers' `kingfisher-process` endpoint:

1. Rename `env.sh.tmpl` to `env.sh`
2. Set the `KINGFISHER_*` variables in `env.sh`.
3. Run `source env.sh` to export them to the scraper environment.

This is *optional*. If you don't set the `KINGFISHER_*` variables, this part of the pipeline is automatically disabled, and scraper results will only be saved to disc.

## Use

```
 scrapy crawl <spider_name> -a key=value
```
eg.

```
 scrapy crawl canada_buyandsell -a sample=true
 scrapy crawl canada_buyandsell
```

## Output

Currently scraped JSON is stored on disc, as it was found. Files are stored in `{project_root}/data/{scraper_name}/{scraper_start_date_time}`. The `/data/` part can be configured in `settings.py` with `FILES_STORE`.

Scrapers also post the downloaded JSON files, and a bunch of metadata, to a [kingfisher-process](https://github.com/open-contracting/kingfisher-process) endpoint (see above for how to configure this).