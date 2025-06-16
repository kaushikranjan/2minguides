import uuid
import random
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, col
from src.utils.products import Products



class PageViewsIngestion:

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.page_views_schema = StructType([
            StructField("event_type", StringType(), True),
            StructField("event_id", StringType(), True),
            StructField("created_ts", TimestampType(), True),
            StructField("session_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("page_url", StringType(), True)
        ])

    def ingest_page_views(self):
        page_views_data = self.create_page_views_data()
        page_views_df = self.spark.createDataFrame(page_views_data, schema=self.page_views_schema)
        page_views_df.show()

        print("Writing page views to Iceberg")
        page_views_df = page_views_df.withColumn(
                "row_num",
                row_number().over(
                    Window.partitionBy("event_id").orderBy(col("created_ts").desc())
                )
            ).filter(col("row_num") == 1).drop("row_num")
        page_views_df.writeTo("nessie.bronze.page_views").append()


    def create_page_views_data(self):
        
        page_views_data = []
        created_ts = datetime.now()
        
        # Generate 10 random page views
        for i in range(10):
            
            # Generate a random user ID and session ID with correlated ranges
            # User IDs are numbered 1-5, and session IDs are grouped by user
            # For example:
            # user1 gets sessions 3-6
            # user2 gets sessions 6-9
            # user3 gets sessions 9-12
            # user4 gets sessions 12-15
            # user5 gets sessions 15-18
            random_int = random.randint(1, 5)

            session_id_start = random_int * 3  # Calculate start of session range based on user number
            session_id_end = (random_int+1) * 3  # Calculate end of session range based on user number
            
            user_id = f"user_{random_int}"  # Create user ID from random number
            session_id = f"session_{random.randint(session_id_start, session_id_end)}"  # Generate session ID within user's range
            page_url = Products().get_random_product_url()  # Create product page URL
            
            # Append page view record with generated data
            log_record = (
                "page_view",  # Event type
                str(uuid.uuid4()),  # Generate unique event ID
                created_ts,  # Format timestamp
                session_id,  # Session identifier
                user_id,  # User identifier
                page_url,  # Product page URL
            )

            page_views_data.append(log_record)

            # Adding duplicate records 5% of the time to simulate data quality issues
            if (random.random() < 0.05):
                page_views_data.append(log_record)
        
        return page_views_data
    
    