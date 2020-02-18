# -*- coding: utf-8 -*-

# Scrapy settings for kingfisher_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'kingfisher_scrapy'

SPIDER_MODULES = ['kingfisher_scrapy.spiders']
NEWSPIDER_MODULE = 'kingfisher_scrapy.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'kingfisher_scrapy (+http://www.open-contracting.org)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 2
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'kingfisher_scrapy.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'kingfisher_scrapy.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}
EXTENSIONS = {
   'kingfisher_scrapy.extensions.KingfisherAPI': 0,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'kingfisher_scrapy.pipelines.KingfisherScrapyPipeline': 300,
#}

KINGFISHER_API_URI = os.environ.get('KINGFISHER_API_URI')
KINGFISHER_API_KEY = os.environ.get('KINGFISHER_API_KEY')
KINGFISHER_API_LOCAL_DIRECTORY = os.environ.get('KINGFISHER_API_LOCAL_DIRECTORY')

# This is used for some legacy environment variables - not needed for new installs
if not KINGFISHER_API_URI and os.environ.get('KINGFISHER_API_FILE_URI'):
    KINGFISHER_API_URI = os.environ.get('KINGFISHER_API_FILE_URI')[:-len('/api/v1/submit/file/')]

KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN = os.environ.get('KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN')
KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET = os.environ.get('KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET')
KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN = os.environ.get('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN')

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# https://docs.scrapy.org/en/latest/topics/media-pipeline.html#std:setting-FILES_STORE
FILES_STORE = 'data'

# https://docs.scrapy.org/en/latest/topics/spider-middleware.html#httperror-allow-all
HTTPERROR_ALLOW_ALL = True
