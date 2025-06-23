from pyspark.sql import SparkSession

class SilverSetup:

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def setup(self):
        # Create the specified namespace
        self.spark.sql(f"""CREATE NAMESPACE IF NOT EXISTS nessie.silver""").show()
        self.spark.sql(f"""DROP TABLE IF EXISTS nessie.silver.page_views""").show() 
        self.spark.sql(f"""DROP TABLE IF EXISTS nessie.silver.click_events""").show()
        self.spark.sql(f"""DROP TABLE IF EXISTS nessie.silver.page_views_agg""").show()
        self.spark.sql(f"""DROP TABLE IF EXISTS nessie.silver.click_events_agg""").show()

        # Create the page_views table
        self.spark.sql(f"""
                       CREATE TABLE nessie.silver.page_views (
                            event_type STRING,
                            event_id STRING,
                            created_ts TIMESTAMP,
                            session_id STRING,
                            page_url STRING,
                            product_id STRING,
                            product_name STRING,
                            product_segment STRING,
                            user_id STRING,
                            user_location STRING,
                            user_gender STRING
                        )
                        USING ICEBERG
                        PARTITIONED BY (bucket(3, event_id))
                       """)
        
        self.spark.sql(f"""
                       CREATE TABLE nessie.silver.page_views_agg (
                            event_type STRING,
                            event_id STRING,
                            created_ts TIMESTAMP,
                            session_id STRING,
                            page_url STRING,
                            product_id STRING,
                            product_name STRING,
                            product_segment STRING,
                            user_id STRING,
                            user_location STRING,
                            user_gender STRING
                        )
                        USING ICEBERG
                        PARTITIONED BY (product_segment, product_id)
                       """)
        
        # Create the click_events table
        self.spark.sql(f"""
                       CREATE TABLE nessie.silver.click_events (
                            event_type STRING,
                            event_id STRING,
                            created_ts TIMESTAMP,
                            session_id STRING,
                            user_id STRING,
                            page_url STRING,
                            product_id STRING,
                            product_name STRING,
                            product_segment STRING,
                            element_id STRING,
                            element_text STRING,
                            element_tag STRING
                        )
                        USING ICEBERG
                        PARTITIONED BY (bucket(3, event_id))
                       """)
        self.spark.sql(f"""
                       CREATE TABLE nessie.silver.click_events_agg (
                            event_type STRING,
                            event_id STRING,
                            created_ts TIMESTAMP,
                            session_id STRING,
                            user_id STRING,
                            page_url STRING,
                            product_id STRING,
                            product_name STRING,
                            product_segment STRING,
                            element_id STRING,
                            element_text STRING,
                            element_tag STRING
                        )
                        USING ICEBERG
                        PARTITIONED BY (product_segment, product_id, element_id))
                       """)