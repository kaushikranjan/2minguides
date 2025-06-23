import os
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from src.utils.sparkudfs import SparkUDFs

class PageViewsTransformation:

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.checkpointBase = os.getenv("WAREHOUSE")
        self.sparkudfs = SparkUDFs(spark)

    def aggregate(self):
        
        # Create a streaming DataFrame from the bronze layer page_views table
        df = self.spark.readStream \
            .format("iceberg") \
            .option("streaming-max-files-per-micro-batch", "1") \
            .load("nessie.silver.page_views")
        
        # Write the streaming DataFrame to the page_views_agg table
        stream = df.writeStream \
            .format("iceberg") \
            .outputMode("append") \
            .option("checkpointLocation", f"{self.checkpointBase}/checkpoint/silver_page_views_agg") \
            .trigger(processingTime='10 seconds') \
            .toTable("nessie.silver.page_views_agg") \
        
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
            input_df.createOrReplaceTempView("page_views_input")
            input_df.persist()
           
            # Extract unique event IDs and format them for SQL IN clause
            event_ids = input_df.select("event_id").distinct().rdd.flatMap(lambda x: x).collect()
            event_ids_str = ",".join(f'"{event_id}"' for event_id in event_ids)

             # Enrich the data with product and user information using UDFs
            # This adds:
            # - Product details (ID, name, segment) extracted from the page URL
            # - User details (location, gender) looked up from the user service
            # //TODO make it into bucket query in pushdown filter
            query = f"""
                MERGE INTO nessie.silver.page_views AS target
                USING ( SELECT 
                            event_type, event_id, created_ts, session_id, page_url,
                            get_product_id(page_url) as product_id,
                            get_product_name(get_product_id(page_url)) as product_name,
                            get_product_segment(get_product_id(page_url)) as product_segment,
                            user_id,
                            get_user_location(user_id) as user_location,
                            get_user_gender(user_id) as user_gender
                            FROM page_views_input
                ) AS source
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
            .load("nessie.bronze.page_views")
        
        
        # Configure and start the streaming job
        stream = df.writeStream \
            .foreachBatch(_upsert) \
            .trigger(processingTime='10 seconds') \
            .option("checkpointLocation", f"{self.checkpointBase}/checkpoint/silver_page_views_transf") \
            .start()
        
        stream.awaitTermination()
        
        
        