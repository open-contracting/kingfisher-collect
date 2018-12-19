# OCDS Scrapy Crawlers

This repo contains crawlers for OCDS data from various publishers, using the [Scrapy](https://scrapy.org/) crawler framework. 

Initially sources are based on those in [OCDS Kingfisher](https://github.com/open-contracting/kingfisher).

## Use
```
 pip install -r requirements.txt 

 scrapy crawl <spider_name> -a key=value
```
Currently implemented:

```
 scrapy crawl canada_buyandsell -a sample=true
 scrapy crawl canada_buyandsell
```

## Output

Currently scraped JSON is stored on disc, as it was found. Files are stored in `{project_root}/data/{scraper_name}/`. The `/data/` part can be configured in `settings.py` with `FILES_STORE`.