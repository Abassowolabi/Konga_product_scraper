BOT_NAME = "konga_products_crawler"

SPIDER_MODULES = ["konga_products_crawler.spiders"]
NEWSPIDER_MODULE = "konga_products_crawler.spiders"

SPLASH_URL = 'http://localhost:8050'

# Remove static User-Agent from DEFAULT_REQUEST_HEADERS or comment it out
DEFAULT_REQUEST_HEADERS = {
    # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
}

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    # add more user agents here...
]

ROBOTSTXT_OBEY = False

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DOWNLOADER_MIDDLEWARES = {
    'konga_products_crawler.middlewares.RandomUserAgentMiddleware': 400,  # custom UA middleware
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # disable default
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10

DOWNLOAD_DELAY = 2

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DATABASE = "konga_scraped_data"

ITEM_PIPELINES = {
    "konga_products_crawler.pipelines.MongoDBPipeline": 300,
}

LOG_LEVEL = 'INFO'
