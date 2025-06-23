from pyspark.sql import SparkSession

class SparkSessionUtils:

    def __init__(self):
        self.spark = SparkSession.builder.getOrCreate()

    def get_spark_session(self):
        return self.spark