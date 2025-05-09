from pyspark.sql import SparkSession, DataFrame


class IcebergReader:

    def __init__(self, namespace: str, table: str, objectStoreBasePath: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.namespace = f'nessie.{namespace}'
        self.table = table
        self.objectStoreBasePath = objectStoreBasePath


    def read(self, interval_seconds: int):

        def _upsert(source_df: DataFrame, _batch_id: int):
            source_df.show(truncate=False)

        stream = self.spark.readStream \
                  .format("iceberg") \
                  .load(f"{self.namespace}.{self.table}")

        stream = stream.writeStream \
            .foreachBatch(_upsert) \
            .trigger(processingTime=f"{interval_seconds} seconds") \
            .option("checkpointLocation",
                    f"{self.objectStoreBasePath}/checkpoint/{self.table}") \
            .start()

        stream.awaitTermination()