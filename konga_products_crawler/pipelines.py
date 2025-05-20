# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import logging
import pymongo

class MongoDBPipeline:
    def open_spider(self, spider):
        self.mongo_uri = spider.settings.get('MONGO_URI', 'mongodb://localhost:27017/')
        self.mongo_db = spider.settings.get('MONGO_DATABASE', 'konga_scraped_data')

        try:
            self.client = pymongo.MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            self.client.admin.command('ping')
            self.db = self.client[self.mongo_db]

            # Use a fixed collection name
            self.collection_name = "all_products"

            # Create unique index on Product_url to avoid duplicates
            self.db[self.collection_name].create_index('Product_url', unique=True)

            logging.info(f"Connected to MongoDB. Using collection: {self.collection_name}")
        except pymongo.errors.ServerSelectionTimeoutError as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise e
        except pymongo.errors.OperationFailure as e:
            logging.error(f"Index creation failed: {e}")

    def close_spider(self, spider):
        self.client.close()
        logging.info("Closed MongoDB connection.")

    def process_item(self, item, spider):
        try:
            self.db[self.collection_name].insert_one(dict(item))
            logging.debug(f"Inserted item into MongoDB: {item.get('Title', 'No Title')}")
        except pymongo.errors.DuplicateKeyError:
            logging.debug(f"Duplicate product found, skipping: {item.get('Product_url')}")
        except Exception as e:
            logging.error(f"Failed to insert item into MongoDB: {e}")
        return item