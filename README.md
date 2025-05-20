
---

# Konga Products Crawler

Welcome to the **Konga Products Crawler** — your trusty, splash-powered Scrapy spider that fearlessly dives into Konga.com, Nigeria’s bustling online marketplace, to scoop up product treasures from beauty, fashion, baby & kids, home & kitchen, and electronics categories! 🚀✨

---

## 🚀 What’s This All About?

This crawler expertly tackles Konga.com’s JavaScript-heavy pages using Splash, extracting essential product info like titles, prices, images, and URLs with accuracy and speed. Built to be reliable and smart, it handles retries, skips empty categories, and navigates pagination smoothly — saving clean, unique data straight into MongoDB for your analysis or projects.

---

## 🎯 What Makes It Awesome?

* **Splash-powered JS rendering** — no more static pages holding you back!
* Scrapes multiple categories one after another, with smart skipping.
* Pagination? Handled smoothly with retry and timeout logic.
* Focuses on top 5 products per page for quality over quantity.
* Pulls out product title, price, URL, and up to 3 dazzling images.
* User-Agent rotation keeps you undercover and stealthy.
* Robust MongoDB pipeline with unique index to dodge duplicates.
* Polite crawler with autothrottle and caching — friendly to Konga’s servers.
* Detailed logs at both INFO and DEBUG levels for full transparency.

---

## 🛠️ How to Get Started — Fast!

1. Clone the repo, jump in:

   ```bash
   git clone https://github.com/yourusername/konga_products_crawler.git
   cd konga_products_crawler
   ```

2. Install dependencies:

   ```bash
   pip install scrapy scrapy-splash pymongo
   ```

3. Fire up Splash (Docker makes it easy):

   ```bash
   docker run -p 8050:8050 scrapinghub/splash
   ```

4. Ensure MongoDB is running locally or remotely (default URI: `mongodb://localhost:27017/`).

5. Tweak settings if you want (like `DOWNLOAD_DELAY`, User-Agent list, or MongoDB URI).

6. Run the spider and watch the magic:

   ```bash
   scrapy crawl konga_spider
   ```

---

## 📸 Snapshots & Demo

### Spider Running

![Spider Running](snapshots/konga_snapshot.PNG)

### Sample Scraped Data in MongoDB

![MongoDB Data](snapshots/konga_snapshot_mongo.PNG)

---

## 🧩 Project Structure Highlights

* **Spider:** `konga_spider.py`
  Starts with 5 category URLs. Sequentially requests pages with Splash rendering. Parses product URLs and limits scraping to 5 products per page. Extracts product details with graceful retry on failures. Skips empty pages or entire categories if configured. Yields items for MongoDB storage.

* **Settings:** `settings.py`
  Configures Splash URL and middleware. Enables caching, autothrottle, retries. Disables obeying robots.txt for full crawl freedom. Includes a rotating User-Agent list to mimic real users. Sets MongoDB connection parameters. Enables MongoDB pipeline to save scraped items.

* **Middleware:** `middlewares.py`
  Custom `RandomUserAgentMiddleware` to assign random User-Agent on each request. Default spider and downloader middleware stubs for potential future extensions. Integrates Splash middleware to handle JS rendering and cookies.

* **Pipeline:** `pipelines.py`
  Connects to MongoDB with retry and timeout settings. Creates unique index on `Product_url` to avoid duplicate records. Inserts each product item and skips duplicates with logs. Closes MongoDB connection cleanly when spider finishes.

---

## ⚠️ Challenges & How I Overcame Them

* **Splash timing out on slow pages**
  Some category pages loaded slowly, causing timeouts. I increased the wait time and added retry logic to keep the scraper running smoothly.

* **Duplicate products in MongoDB**
  I saw repeated entries at first, so I tracked seen URLs in memory and created a unique index on `Product_url` in MongoDB to prevent duplicates.

* **Getting stuck on empty categories**
  The spider would loop endlessly when a category had no products. Adding a check to skip empty categories helped keep the crawl moving forward.

* **Scraping merchant pages by mistake**
  Some links pointed to merchant profiles instead of products. I refined the XPath to only grab URLs containing `/product/` to target actual products.

* **Splash container crashing after many requests**
  The Splash Docker container would disconnect after about 300 requests. I reduced requests per page, added delays, and restarted the container when needed.

* **Finding the right amount of data**
  Trying to scrape 5,000 products was too slow and caused crashes. I scaled back to around 2,500 products, which still provides solid data for testing and demos.

---

## 🧠 Notes & Tips

* Modify `categories_to_skip` list in the spider to exclude any category URLs you don’t want scraped.
* Adjust `DOWNLOAD_DELAY` and `AUTOTHROTTLE` settings to balance speed and server friendliness.
* MongoDB collection is fixed to `all_products`, but you can change this in the pipeline.
* Extend the User-Agent list in settings for better anti-blocking.
* Use Docker for Splash for easy installation and environment consistency.
* Logs at DEBUG level give detailed request/response info for troubleshooting.

---

## 🏆 Why You’ll Love This Project

Because it’s not just another scraper — it’s a battle-tested, splash-enhanced crawler ready to take on complex JS sites, armed with retries, smart logic, and a knack for keeping data clean. It’s a perfect foundation for your next data-driven project or to learn how pro-grade scraping really works.

---

## 👨‍💻 Contribution

Feel free to fork, improve, and submit pull requests! Whether it’s adding more categories, improving error handling, or optimizing the pipeline, your contributions are welcome.

---

## 📜 License

MIT License — free to use, modify, and share

---

