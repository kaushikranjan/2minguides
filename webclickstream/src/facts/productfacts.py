import os
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import date_format, date_trunc, count, struct, lit

class ProductFacts:

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.checkpointBase = os.getenv("WAREHOUSE")

    def create_product_facts_from_page_view(self):

        # Define a function to handle each batch of data
        def _upsert(input_df: DataFrame, _batch_id: int):

            input_df = input_df.withColumn("minute_ts", date_trunc("minute", "created_ts"))
            input_df.createOrReplaceTempView("page_views_input")
            input_df = input_df.sparkSession.sql("""
                SELECT 
                    minute_ts, product_id, product_name, product_segment,
                    COUNT(*) as counts, 'views' as count_type,
                    STRUCT('' AS element_id, '' AS element_text) as click
                FROM page_views_input
                GROUP BY 
                    minute_ts,
                    product_segment,
                    product_name,
                    product_id
            """)
            input_df.writeTo("nessie.gold.fact_product_metrics").append()

           
        # Create a streaming DataFrame from the bronze layer page_views table
        pageviews_df = self.spark.readStream \
            .format("iceberg") \
            .option("streaming-max-files-per-micro-batch", "1") \
            .load("nessie.silver.page_views_agg")

        stream = pageviews_df.writeStream \
            .foreachBatch(_upsert) \
            .trigger(processingTime='1 seconds') \
            .option("checkpointLocation", f"{self.checkpointBase}/checkpoint/gold_fact_product_metrics_page_views") \
            .start()
        
        stream.awaitTermination()

    def create_product_facts_from_click_events(self):

        # Define a function to handle each batch of data
        def _upsert(input_df: DataFrame, _batch_id: int):

            input_df = input_df.withColumn("minute_ts", date_trunc("minute", "created_ts"))
            input_df.createOrReplaceTempView("click_events_input")
            input_df = input_df.sparkSession.sql("""
                SELECT 
                    minute_ts, product_id, product_name, product_segment,
                    COUNT(*) as counts, 'clicks' as count_type,
                    STRUCT(element_id, element_text) as click
                FROM click_events_input
                GROUP BY 
                    minute_ts,
                    product_segment,
                    product_name,
                    product_id,
                    element_id,
                    element_text
            """)
            input_df.writeTo("nessie.gold.fact_product_metrics").append()

           
        # Create a streaming DataFrame from the bronze layer page_views table
        clickevents_df = self.spark.readStream \
            .format("iceberg") \
            .option("streaming-max-files-per-micro-batch", "1") \
            .load("nessie.silver.click_events_agg")

        stream = clickevents_df.writeStream \
            .foreachBatch(_upsert) \
            .trigger(processingTime='1 seconds') \
            .option("checkpointLocation", f"{self.checkpointBase}/checkpoint/gold_fact_product_metrics_click_events") \
            .start()
        
        stream.awaitTermination()