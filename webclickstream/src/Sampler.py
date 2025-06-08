from faker import Faker
import random
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from pyspark.sql import SparkSession

class Sampler:

    def __init__(self, namespace: str, table: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.namespace = f'nessie.{namespace}'
        self.table = table

    def sample(self):
        
        
        # Create Faker instance
        fake = Faker()

        # Generate sample data
        data = [(fake.user_name(), random.randint(18, 80)) for _ in range(100)]

        # Define schema
        schema = StructType([
            StructField("username", StringType(), True),
            StructField("age", IntegerType(), True)
        ])

        # Create DataFrame
        df = self.spark.createDataFrame(data, schema)
        df.show()

        # Create the specified namespace
        self.spark.sql(f"""CREATE NAMESPACE IF NOT EXISTS {self.namespace}""")
        
        # Write the DataFrame to Iceberg table in the specified namespace
        df.writeTo(f"{self.namespace}.{self.table}").using("iceberg").create()
        
        # Print the records in the table
        print(f"Records in {self.namespace}.{self.table}:")
        self.spark.read.format("iceberg").load(f"{self.namespace}.{self.table}").limit(10).show()