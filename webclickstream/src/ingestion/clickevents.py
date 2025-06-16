import uuid
import random
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col
from src.utils.products import Products


class ClickEventsIngestion:

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.click_events_schema = StructType([
            StructField("event_type", StringType(), True),
            StructField("event_id", StringType(), True),
            StructField("created_ts", TimestampType(), True),
            StructField("session_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("page_url", StringType(), True),
            StructField("element_id", StringType(), True),
            StructField("element_text", StringType(), True),
            StructField("element_tag", StringType(), True)
        ])

    def ingest_click_events(self):
        click_events_data = self.create_click_events_data()
        click_events_df = self.spark.createDataFrame(click_events_data, schema=self.click_events_schema)
        click_events_df.show()

        print("Writing click events to Iceberg")
        click_events_df = click_events_df.withColumn(
                "row_num",
                row_number().over(
                    Window.partitionBy("event_id").orderBy(col("created_ts").desc())
                )
            ).filter(col("row_num") == 1).drop("row_num")
        click_events_df.writeTo("nessie.bronze.click_events").append()


    def create_click_events_data(self):
    
        # Generate 30 random page views
        click_events_data = []
        base_time = datetime.now()
        
        for _ in range(30):
            timestamp = base_time

            # Generate a random user ID and session ID with correlated ranges
            random_int = random.randint(1, 5)
            session_id_start = random_int * 3
            session_id_end = (random_int+1) * 3
            
            user_id = f"user_{random_int}"
            session_id = f"session_{random.randint(session_id_start, session_id_end)}"
            
            # Generate random product ID and page URL
            page_url = Products().get_random_product_url()  # Create product page URL
            
            # Generate random element data for click events
            element_ids = ["add-to-cart", "buy-now", "wishlist", "product-image", "product-description"]
            element_texts = ["Add to Cart", "Buy Now", "Add to Wishlist", "Product Image", "View Details"]
            element_tags = ["button", "button", "button", "img", "a"]
            
            element_index = random.randint(0, len(element_ids) - 1)
            
            # Append click event record with generated data
            click_events_data.append((
                "click_event",  # Event type
                str(uuid.uuid4()),  # Generate unique event ID
                timestamp,  # Format timestamp
                session_id,  # Session identifier
                user_id,  # User identifier
                page_url,  # Product page URL
                element_ids[element_index],  # Clicked element ID
                element_texts[element_index],  # Clicked element text
                element_tags[element_index]  # Clicked element HTML tag
            ))

        return click_events_data
            
           