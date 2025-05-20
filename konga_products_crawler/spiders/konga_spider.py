import scrapy
import re
from scrapy_splash import SplashRequest

class KongaSpider(scrapy.Spider):
    name = "konga_spider"
    allowed_domains = ["konga.com"]

    # List of category URLs to scrape
    start_urls = [
        "https://www.konga.com/category/beauty-health-personal-care-4",
        "https://www.konga.com/category/konga-fashion-1259",
        "https://www.konga.com/category/baby-kids-toys-8",
        "https://www.konga.com/category/home-kitchen-602",
        "https://www.konga.com/category/electronics-5261"
    ]

    # Custom settings specific to this spider
    custom_settings = {
        'SPLASH_COOKIES_DEBUG': False,
        'HTTPCACHE_ENABLED': True,
        'SPLASH_WAIT': 5,
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'DEBUG',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scraped_count = 0  # Count of total scraped products

        # Optional: slugs of categories to skip (manually specified)
        self.categories_to_skip = []

    def start_requests(self):
        self.logger.info("Starting categories scraping sequentially...")

        self.category_index = 0
        self.current_page = 1
        self.seen_product_urls = set()  # To avoid scraping the same product twice

        # Skip any categories in the skip list
        while self.category_index < len(self.start_urls):
            url = self.start_urls[self.category_index]
            slug = url.split('/')[-1]

            if slug in self.categories_to_skip:
                self.logger.info(f"Skipping category: {slug}")
                self.category_index += 1
            else:
                break

        # Begin scraping the first eligible category
        if self.category_index < len(self.start_urls):
            yield self.request_category_page(self.category_index, self.current_page)
        else:
            self.logger.info("All categories were skipped.")

    def request_category_page(self, category_index, page, retry_count=0):
        # Builds a paginated request for a category using Splash
        base_url = self.start_urls[category_index]
        page_url = base_url if page == 1 else f"{base_url}?page={page}"
        self.logger.debug(f"Requesting category page {page} of category {base_url}")
        return SplashRequest(
            url=page_url,
            callback=self.parse,
            args={'wait': self.custom_settings['SPLASH_WAIT']},
            meta={
                'category_index': category_index,
                'page': page,
                'retry_count': retry_count,
            },
            errback=self.handle_splash_error,
            endpoint='render.html',
            dont_filter=True
        )

    def handle_splash_error(self, failure):
        # Handles errors from Splash (timeouts, crashes, etc.)
        self.logger.error(f"Splash error: {repr(failure)}")
        meta = failure.request.meta or {}

        retry_count = meta.get('retry_count', 0)
        category_index = meta.get('category_index', None)
        page = meta.get('page', None)

        if category_index is None or page is None:
            self.logger.error("Missing 'category_index' or 'page' in meta; cannot retry request.")
            return

        # Retry up to 2 times on Splash errors
        if retry_count < 2:
            self.logger.warning(f"Retrying category page due to Splash failure (attempt {retry_count + 1})")
            yield self.request_category_page(
                category_index=category_index,
                page=page,
                retry_count=retry_count + 1
            )
        else:
            self.logger.error("Max retry attempts reached for Splash failure.")

    def parse(self, response):
        # Handles parsing of each category page
        category_index = response.meta['category_index']
        page = response.meta['page']
        category_url = self.start_urls[category_index]
        retry_count = response.meta.get('retry_count', 0)

        self.logger.info(f"Parsing category {category_url} page {page}")

        # Extract raw product URLs from the category page
        raw_product_urls = response.xpath('//a[contains(@href, "/product/")]/@href').getall()
        product_urls = list(set(raw_product_urls))  # Remove duplicates

        # If no products found, retry or move to next category
        if not product_urls:
            if retry_count < 2:
                self.logger.warning(f"No products found on page {page} of {category_url}. Retrying (attempt {retry_count + 1})...")
                yield self.request_category_page(category_index, page, retry_count + 1)
                return

            self.logger.info(f"No products found on page {page} of category {category_url}. Moving to next category.")
            next_category_index = category_index + 1

            while next_category_index < len(self.start_urls):
                next_slug = self.start_urls[next_category_index].split('/')[-1]
                if next_slug in self.categories_to_skip:
                    self.logger.info(f"Skipping category: {next_slug}")
                    next_category_index += 1
                else:
                    break

            if next_category_index < len(self.start_urls):
                self.current_page = 1
                yield self.request_category_page(next_category_index, self.current_page)
            else:
                self.logger.info("No more categories to scrape.")
            return

        # Deduplicate and collect product URLs
        new_urls = []
        for url in product_urls:
            full_url = response.urljoin(url)
            if full_url not in self.seen_product_urls:
                self.seen_product_urls.add(full_url)
                new_urls.append(full_url)

        self.logger.debug(f"Found {len(new_urls)} unique new product URLs on page {page} of category {category_url}")

        # ✅ Limit to only 5 products per page
        limited_product_urls = new_urls[:5]

        # Request each product page with Splash
        for absolute_url in limited_product_urls:
            yield SplashRequest(
                url=absolute_url,
                callback=self.parse_page,
                meta={'product_url': absolute_url, 'category_url': category_url},
                args={'wait': self.custom_settings['SPLASH_WAIT']},
                errback=self.handle_splash_error,
                endpoint='render.html',
                dont_filter=True
            )

        # Check if there's a "Next" button, go to next page if exists
        has_next = response.xpath('//a[contains(text(), "Next")]').get()
        if has_next:
            next_page = page + 1
            yield self.request_category_page(category_index, next_page)
        else:
            self.logger.info(f"'Next' button not found on page {page} of category {category_url}. Moving to next category.")
            next_category_index = category_index + 1

            while next_category_index < len(self.start_urls):
                next_slug = self.start_urls[next_category_index].split('/')[-1]
                if next_slug in self.categories_to_skip:
                    self.logger.info(f"Skipping category: {next_slug}")
                    next_category_index += 1
                else:
                    break

            if next_category_index < len(self.start_urls):
                self.current_page = 1
                yield self.request_category_page(next_category_index, self.current_page)
            else:
                self.logger.info("No more categories to scrape.")

    def parse_page(self, response):
        # Extract details from individual product pages
        if response.status != 200:
            self.logger.error(f"Bad response status {response.status} for product page: {response.url}")
            return

        product_url = response.meta.get('product_url')
        category_url = response.meta.get('category_url')
        self.logger.info(f"Parsing product: {product_url}")

        # Extract product title
        title = response.xpath('//title/text()').get()
        title = title.split(' | ')[0].strip() if title else 'No Title'

        # Try to extract price using various selectors
        currency = response.xpath('//div/span[contains(@style, "font-family")]/text()').get()
        amount = response.xpath('//div[span[contains(@style, "font-family")]]/text()').get()

        if currency and amount:
            price = currency.strip() + amount.strip()
        else:
            full_price_text = response.xpath('//span[contains(@style, "font-family")]/text()').get()
            if full_price_text:
                match = re.search(r'₦\s?[\d,]+', full_price_text)
                price = match.group(0) if match else 'No Price'
            else:
                price = 'No Price'

        # Skip incomplete product info
        if title == 'No Title' or price == 'No Price':
            self.logger.warning(f"Skipping product due to missing title or price: {product_url}")
            return

        # Extract and deduplicate product image URLs
        product_imgs = response.xpath('//img[contains(@src, "/product/")]/@src').getall()
        seen = set()
        unique_imgs = []
        for img in product_imgs:
            if img not in seen:
                unique_imgs.append(img)
                seen.add(img)

        # Limit to top 3 images per product
        product_images = unique_imgs[:3] if unique_imgs else []

        if not product_images:
            self.logger.warning(f"No images found on product page: {product_url}")

        self.logger.debug(f"Extracted {len(product_images)} unique image(s) for product: {product_url}")

        self.scraped_count += 1
        self.logger.info(f"Scraped products so far: {self.scraped_count}")

        # Yield the final product data
        yield {
            'Title': title,
            'Price': price,
            'Product_url': product_url,
            'Images': product_images,
            'Category': category_url
        }
