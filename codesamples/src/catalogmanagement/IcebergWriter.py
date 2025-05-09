from pyspark.sql import SparkSession
from faker import Faker
import random
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

class IcebergWriter:

    def __init__(self, namespace: str, table: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.namespace = f'nessie.{namespace}'
        self.table = table
        self.faker = Faker()
        self.categories = ["electronics", "clothing", "home-garden", "books", "fitness", "toys"]

    def setup(self):

        self.spark.sql(f"""CREATE NAMESPACE IF NOT EXISTS {self.namespace}""").show()

        self.spark.sql(f"""DROP TABLE IF EXISTS {self.namespace}.{self.table}""").show()

        self.spark.sql(f"""
            CREATE TABLE {self.namespace}.{self.table} (
                ip STRING,
                url STRING,
                user_agent STRING,
                referrer STRING,
                created_on TIMESTAMP
            )
            USING ICEBERG
        """)

    def generate_custom_product_url(self):
        category = random.choice(self.categories)
        product_name = self.faker.slug()
        return f"https://shoptillyoudrop.com/products/{category}/{product_name}"

    def generate_fake_record(self):
        return (
            self.faker.ipv4_public(),
            self.generate_custom_product_url(),
            self.faker.user_agent(),
            self.faker.url(),
            self.faker.date_time_between(start_date='-50d', end_date='now')
        )

    def append(self):
        # Create a list of records
        num_records = 100  # adjust as needed
        data = [self.generate_fake_record() for _ in range(num_records)]

        # Define the schema
        schema = StructType([
            StructField("ip", StringType(), True),
            StructField("url", StringType(), True),
            StructField("user_agent", StringType(), True),
            StructField("referrer", StringType(), True),
            StructField("created_on", TimestampType(), True)
        ])

        # Create DataFrame
        df = self.spark.createDataFrame(data, schema)

        # Write Dataframe to Iceberg
        df.write.format("iceberg") \
            .mode("append") \
            .save(f"{self.namespace}.{self.table}")

