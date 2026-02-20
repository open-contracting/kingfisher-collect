# Scrapy settings for kingfisher_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import os

BOT_NAME = "kingfisher_scrapy"

SPIDER_MODULES = ["kingfisher_scrapy.spiders"]
NEWSPIDER_MODULE = "kingfisher_scrapy.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "kingfisher_scrapy (+http://www.open-contracting.org)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # default False, template True

# Concurrency and throttling settings
CONCURRENT_REQUESTS = 32  # default 16
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # default 8, template 1
# DOWNLOAD_DELAY = 1  # default 0, template 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#    'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    # https://docs.scrapy.org/en/latest/topics/spider-middleware.html#topics-spider-middleware-setting
    # `process_spider_output` is invoked in decreasing order.
    "kingfisher_scrapy.spidermiddlewares.ConcatenatedJSONMiddleware": 600,
    "kingfisher_scrapy.spidermiddlewares.LineDelimitedMiddleware": 500,
    "kingfisher_scrapy.spidermiddlewares.ValidateJSONMiddleware": 450,
    "kingfisher_scrapy.spidermiddlewares.RootPathMiddleware": 400,
    "kingfisher_scrapy.spidermiddlewares.AddPackageMiddleware": 300,
    "kingfisher_scrapy.spidermiddlewares.ResizePackageMiddleware": 200,
    "kingfisher_scrapy.spidermiddlewares.ReadDataMiddleware": 100,
    "kingfisher_scrapy.spidermiddlewares.RetryDataErrorMiddleware": 50,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": None,
    "kingfisher_scrapy.downloadermiddlewares.DelayedRequestMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    "kingfisher_scrapy.extensions.SentryLogging": -1,
    "kingfisher_scrapy.extensions.Pluck": 1,
    # `FilesStore` must run before `KingfisherProcessAPI2`, because the file needs to be written before the
    # request is sent to Kingfisher Process.
    "kingfisher_scrapy.extensions.FilesStore": 100,
    "kingfisher_scrapy.extensions.KingfisherProcessAPI2": 500,
    "kingfisher_scrapy.extensions.ItemCount": 600,
    "kingfisher_scrapy.extensions.DatabaseStore": 700,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "kingfisher_scrapy.pipelines.Sample": 200,
    "kingfisher_scrapy.pipelines.Unflatten": 300,
    "kingfisher_scrapy.pipelines.Validate": 301,
    "kingfisher_scrapy.pipelines.Pluck": 302,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# Project-specific Scrapy configuration

logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
logging.getLogger("requests_cache.backends").setLevel(logging.INFO)
logging.getLogger("requests_cache.policy.actions").setLevel(logging.INFO)

# https://docs.scrapy.org/en/latest/topics/settings.html#std-setting-DOWNLOAD_TIMEOUT
DOWNLOAD_TIMEOUT = 360  # many spiders time out when using the 180 default
# https://docs.scrapy.org/en/latest/topics/settings.html#download-maxsize
DOWNLOAD_MAXSIZE = 10000000000  # 10 GB, default 1 GiB
# https://docs.scrapy.org/en/latest/topics/settings.html#download-warnsize
DOWNLOAD_WARNSIZE = 0  # default 32 MiB

# https://docs.scrapy.org/en/latest/topics/spider-middleware.html#httperror-allow-all
HTTPERROR_ALLOW_ALL = True  # default False

# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpproxy-enabled
HTTPPROXY_ENABLED = False  # default True
# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#retry-http-codes
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408]  # handle 429 separately

# https://docs.scrapy.org/en/latest/topics/settings.html#log-formatter
LOG_FORMATTER = "kingfisher_scrapy.log_formatter.LogFormatter"

# Scrapyd won't have (and doesn't need) access to this module.
if os.getenv("SCRAPY_PROJECT") is None:
    # https://docs.scrapy.org/en/latest/topics/commands.html#std-setting-COMMANDS_MODULE
    COMMANDS_MODULE = "kingfisher_scrapy.commands"


# Project configuration

# Add the names of spiders that need to use a proxy.
PROXY_SPIDERS = os.getenv("PROXY_SPIDERS")

# To send exceptions and log records to Sentry.
# Used by SentryLogging extension.
SENTRY_DSN = os.getenv("SENTRY_DSN")

# This setting is not the same as the Scrapy setting. (The project previously used FilesPipeline.)
# Used by FilesStore extension.
FILES_STORE = os.getenv("FILES_STORE", "data")

# To store items into a PostgreSQL database.
# Used by DatabaseStore extension.
DATABASE_URL = None

# To send items to Kingfisher Process (version 2).
# Used by KingfisherProcessAPI2 extension.
KINGFISHER_API2_URL = os.getenv("KINGFISHER_API2_URL")
RABBIT_URL = os.getenv("RABBIT_URL")
RABBIT_EXCHANGE_NAME = os.getenv("RABBIT_EXCHANGE_NAME")
RABBIT_ROUTING_KEY = os.getenv("RABBIT_ROUTING_KEY")

# Used by Pluck extension.
KINGFISHER_PLUCK_PATH = os.getenv("KINGFISHER_PLUCK_PATH", "")
KINGFISHER_PLUCK_MAX_BYTES = None


# API keys

KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN = os.getenv("KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN")
KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET = os.getenv("KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET")

# To get an API account, visit https://www.contrataciones.gov.py/datos/adm/signup
KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN = os.getenv("KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN")
