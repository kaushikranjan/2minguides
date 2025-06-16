from pyspark.sql import SparkSession

class BronzeSetup:

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def setup(self):
        # Create the specified namespace
        self.spark.sql(f"""CREATE NAMESPACE IF NOT EXISTS nessie.bronze""").show()
        self.spark.sql(f"""DROP TABLE IF EXISTS nessie.bronze.page_views""").show()
        self.spark.sql(f"""DROP TABLE IF EXISTS nessie.bronze.click_events""").show()

        # Create the page_views table
        self.spark.sql(f"""
                       CREATE TABLE nessie.bronze.page_views (
                            event_type STRING,
                            event_id STRING,
                            created_ts TIMESTAMP,
                            session_id STRING,
                            user_id STRING,
                            page_url STRING
                        )
                        USING ICEBERG
                        PARTITIONED BY (bucket(3, event_id))
                       """)
        
        # Create the click_events table
        self.spark.sql(f"""
                       CREATE TABLE nessie.bronze.click_events (
                            event_type STRING,
                            event_id STRING,
                            created_ts TIMESTAMP,
                            session_id STRING,
                            user_id STRING,
                            page_url STRING,
                            element_id STRING,
                            element_text STRING,
                            element_tag STRING
                        )
                        USING ICEBERG
                        PARTITIONED BY (bucket(3, event_id))
                       """)