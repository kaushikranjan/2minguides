from src.ddl.CatalogUtils import CatalogUtils
from pyspark.sql import SparkSession
from typing import Dict

class TableUtils:

    def __init__(self, namespace_str: str, table_str: str):
        self.catalog = CatalogUtils(namespace_str)
        self.table = table_str
        self.spark = SparkSession.builder.getOrCreate()

    def get_table(self):
        return f"{self.catalog.get_namespace()}.{self.table}"

    def create_table(self, column_definition: Dict[str, str]):
        columns = []
        for key, value in column_definition.items():
            columns.append(f"{key} {value}")
        columns = ",".join(columns)

        self.spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.get_table()} ({columns})
            USING ICEBERG
        """)
