from src.services.userservice import UserService
from src.services.productservice import ProductService
from src.utils.products import Products
from pyspark.sql import SparkSession


class SparkUDFs:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        
        
    def register_udfs(self):
        # Register UDF to generate product specific fields
        self.spark.udf.register(
            "get_product_id",
            lambda url: Products().strip_product_url(url)
        )
        
        self.spark.udf.register(
            "get_product_name",
            lambda url: ProductService().get_product_details(Products().strip_product_url(url))["product_name"]
        )
        
        self.spark.udf.register(
            "get_product_segment",
            lambda url: ProductService().get_product_details(Products().strip_product_url(url))["product_segment"]
        )

        # Register UDF to generate user specific fields
        self.spark.udf.register(
            "get_user_location",
            lambda user_id: UserService().generate_user_attributes(user_id)["user_location"]
        )
        
        self.spark.udf.register(
            "get_user_age",
            lambda user_id:  UserService().generate_user_attributes(user_id)["user_age"]
        )
        
        self.spark.udf.register(
            "get_user_gender",
            lambda user_id: UserService().generate_user_attributes(user_id)["user_gender"]
        )