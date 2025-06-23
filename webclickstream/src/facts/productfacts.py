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
            
            input_df.persist()
            modified_df = input_df.withColumn("minute_ts", date_trunc("minute", "created_ts"))
            modified_df.createOrReplaceTempView("page_views_input")
            grouped_df = modified_df.sparkSession.sql("""
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

            def compact(input_df: DataFrame):
                unique_keys_df = input_df.select(
                    "minute_ts", "product_segment", "product_name", "product_id"
                ).distinct()

                # Collect combinations (assumes limited number per micro-batch)
                unique_keys = unique_keys_df.collect()
                print("rahul-keys", unique_keys)

                for row in unique_keys:
                    minute_ts = row["minute_ts"]
                    product_segment = row["product_segment"]
                    product_id = row["product_id"]
                    

                    # Build WHERE clause for targeted compaction
                    where_clause = (
                        f"minute_ts = TIMESTAMP '{minute_ts}' AND "
                        f"product_segment = '{product_segment}' AND "
                        f"product_id = '{product_id}' AND "
                        f"count_type = 'views'"
                    )

                    print(f"Compacting partition: {where_clause}")

                    minFileSizeBytes = 384 * 1024 * 1024 # 384 MB i.e 0.75 of 512 MB
                    maxFileSizeBytes = 896 * 1024 * 1024  # 896 MB i.e. 1.75 of 512MB
                    targetFileSizeBytes = 512 * 1024 * 1024 # 512 MB
                    minInputFiles = 1
                    # Run compaction for the partition
                    input_df.sparkSession.sql(f"""
                        CALL nessie.system.rewrite_data_files(
                            table => 'nessie.gold.fact_product_metrics',
                            where => "{where_clause}",
                            options => map(
                                'min-file-size-bytes', '{minFileSizeBytes}',
                                'max-file-size-bytes', '{maxFileSizeBytes}',
                                'target-file-size-bytes', '{targetFileSizeBytes}',
                                'min-input-files', '{minInputFiles}',
                                'use-starting-sequence-number', 'false'
                            )
                        )
                    """)
            
            compact(grouped_df)

            grouped_df.writeTo("nessie.gold.fact_product_metrics").append()
            input_df.unpersist()

           
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

            input_df.persist()

            modified_df = input_df.withColumn("minute_ts", date_trunc("minute", "created_ts"))
            modified_df.createOrReplaceTempView("click_events_input")
            grouped_df = modified_df.sparkSession.sql("""
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

            def compact(input_df: DataFrame):
                unique_keys_df = input_df.select(
                    "minute_ts", "product_segment", "product_name", "product_id"
                ).distinct()

                # Collect combinations (assumes limited number per micro-batch)
                unique_keys = unique_keys_df.collect()
                print("rahul-keys", unique_keys)

                for row in unique_keys:
                    minute_ts = row["minute_ts"]
                    product_segment = row["product_segment"]
                    product_name = row["product_name"]
                    product_id = row["product_id"]
                    
                    # Build WHERE clause for targeted compaction
                    where_clause = (
                        f"minute_ts = TIMESTAMP '{minute_ts}' AND "
                        f"product_segment = '{product_segment}' AND "
                        f"product_id = '{product_id}' AND "
                        f"count_type = 'clicks'"
                    )
                    print("rahul-values", where_clause)

                    print(f"Compacting partition: {where_clause}")
                    minFileSizeBytes = 384 * 1024 * 1024 # 384 MB i.e 0.75 of 512 MB
                    maxFileSizeBytes = 896 * 1024 * 1024  # 896 MB i.e. 1.75 of 512MB
                    targetFileSizeBytes = 512 * 1024 * 1024 # 512 MB
                    minInputFiles = 1
                    # Run compaction for the partition
                    input_df.sparkSession.sql(f"""
                        CALL nessie.system.rewrite_data_files(
                            table => 'nessie.gold.fact_product_metrics',
                            where => "{where_clause}",
                            options => map(
                                'min-file-size-bytes', '{minFileSizeBytes}',
                                'max-file-size-bytes', '{maxFileSizeBytes}',
                                'target-file-size-bytes', '{targetFileSizeBytes}',
                                'min-input-files', '{minInputFiles}',
                                'use-starting-sequence-number', 'false'
                            )
                        )
                    """)
            
            grouped_df.writeTo("nessie.gold.fact_product_metrics").append()
            compact(grouped_df)
            
            input_df.unpersist()

            

           
        # Create a streaming DataFrame from the bronze layer page_views table
        clickevents_df = self.spark.readStream \
            .format("iceberg") \
            .option("streaming-max-files-per-micro-batch", "1") \
            .load("nessie.silver.click_events_agg")

        stream = clickevents_df.writeStream \
            .foreachBatch(_upsert) \
            .trigger(processingTime='1 seconds') \
            .option("checkpointLocation", f"{self.checkpointBase}/checkpoint/gold_fact_product_metrics_clicks") \
            .start()
        
        stream.awaitTermination()
