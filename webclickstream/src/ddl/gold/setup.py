from pyspark.sql import SparkSession

class GoldSetup:

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def setup(self):
        # Create the specified namespace
        self.spark.sql(f"""CREATE NAMESPACE IF NOT EXISTS nessie.gold""").show()
        self.spark.sql(f"""DROP TABLE IF EXISTS nessie.gold.fact_product_metrics""").show()
        
        # Create the fact_page_metrics table
        self.spark.sql(f"""
                       CREATE TABLE nessie.gold.fact_product_metrics (
                            minute_ts TIMESTAMP,
                            product_id STRING,
                            product_name STRING,
                            product_segment STRING,
                            counts LONG,
                            count_type STRING,
                            click STRUCT<element_id: STRING, element_text: STRING>
                        )
                        USING ICEBERG
                        PARTITIONED BY (product_segment, product_id, count_type, minute_ts)
                       """)
        self.spark.sql(f"""
                        ALTER TABLE nessie.gold.fact_product_metrics 
                        WRITE ORDERED BY product_id ASC
                       """)