from pyspark.sql import SparkSession

class CatalogUtils:

    def __init__(self, namespace_str: str):
        self.catalog = "nessie"
        self.namespace = namespace_str
        self.spark = SparkSession.builder.getOrCreate()

    def get_namespace(self):
        return f"{self.catalog}.{self.namespace}"

    def create_namespace(self):
        self.spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {self.get_namespace()}")

