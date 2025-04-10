from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType

# Create a SparkSession
spark = SparkSession.builder.appName("FriendsExample").getOrCreate()

# Define some data - list of friends
data = [("Alice",), ("Bob",), ("Charlie",)]

# Define schema
schema = StructType([StructField("Name", StringType(), True)])

# Create DataFrame
friends_df = spark.createDataFrame(data, schema)

# Show the DataFrame
friends_df.show()