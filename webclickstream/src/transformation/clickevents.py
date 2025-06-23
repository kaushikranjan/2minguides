import os
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from src.utils.sparkudfs import SparkUDFs

class ClickEventsTransformation:

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.checkpointBase = os.getenv("WAREHOUSE")
        self.sparkudfs = SparkUDFs(spark)

    def aggregate(self):
        
        # Create a streaming DataFrame from the bronze layer page_views table
        df = self.spark.readStream \
            .format("iceberg") \
            .option("streaming-max-files-per-micro-batch", "1") \
            .load("nessie.silver.click_events")
        
        # Write the streaming DataFrame to the page_views_agg table
        stream = df.writeStream \
            .format("iceberg") \
            .outputMode("append") \
            .option("checkpointLocation", f"{self.checkpointBase}/checkpoint/silver_click_events_agg") \
            .trigger(processingTime='10 seconds') \
            .toTable("nessie.silver.click_events_agg") \
        
        stream.awaitTermination()
        
    def transform(self):
        # Define a function to handle each batch of data
        def _upsert(input_df: DataFrame, _batch_id: int):

            # Get the Spark session from the input DataFrame
            spark_session = input_df.sparkSession

            # Deduplicate events by keeping only the latest event for each event_id
            # This is done by:
            # 1. Repartitioning by event_id to ensure all events with same ID are in same partition
            # 2. Adding a row number within each event_id partition, ordered by timestamp descending
            # 3. Keeping only the first row (most recent) for each event_id
            
            # Create a temporary view for SQL operations
            input_df.createOrReplaceTempView("click_events_input")
            input_df.persist()
            input_df.explain(True)
           
            # Extract unique event IDs and format them for SQL IN clause
            event_ids = input_df.select("event_id").distinct().rdd.flatMap(lambda x: x).collect()
            event_ids_str = ",".join(f'"{event_id}"' for event_id in event_ids)  

            query = f"""
                MERGE INTO nessie.silver.click_events AS target
                USING ( SELECT 
                            event_type, event_id, created_ts, session_id, user_id, page_url,
                            get_product_id(page_url) as product_id,
                            get_product_name(page_url) as product_name,
                            get_product_segment(page_url) as product_segment,
                            element_id,
                            element_text,
                            element_tag
                            FROM click_events_input ) AS source
                ON target.event_id IN ({event_ids_str})
                AND target.event_id = source.event_id
                WHEN NOT MATCHED THEN INSERT *
            """
            print(query)
            output_df = spark_session.sql(query)
            output_df.show()
            output_df.explain(True)
            input_df.unpersist()

        # Register UDFs
        self.sparkudfs.register_udfs()

        # Create a streaming DataFrame from the bronze layer page_views table
        df = self.spark.readStream \
            .format("iceberg") \
            .option("streaming-max-files-per-micro-batch", "1") \
            .load("nessie.bronze.click_events")
        
        
        # Configure and start the streaming job
        stream = df.writeStream \
            .foreachBatch(_upsert) \
            .trigger(processingTime='10 seconds') \
            .option("checkpointLocation", f"{self.checkpointBase}/checkpoint/silver_click_events_transf") \
            .start()
        
        stream.awaitTermination()
        
        