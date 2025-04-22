from faker import Faker

from src.ddl.TableUtils import TableUtils
from pyspark.sql import SparkSession

class FriendTableHandler:

    def __init__(self, namespace: str):
        table = "friends"
        self.faker = Faker()
        self.tableUtils = TableUtils(namespace, table)
        self.spark = SparkSession.builder.getOrCreate()

    def create_friends_table(self):
        self.tableUtils.create_table(column_definition = {
            "name": "STRING",
            "birthday": "DATE",
            "city": "STRING",
            "phone_number": "STRING"
        })

    def add_friends(self):
        friends_data = []
        columns = ["name", "birthday", "city", "phone_number"]

        for _ in range(5):
            name = self.faker.name()
            birthday = self.faker.date_of_birth(minimum_age=18, maximum_age=80)
            city = self.faker.city()
            phone_number = self.faker.phone_number()

            friends_data.append((name, birthday, city, phone_number))

        df = self.spark.createDataFrame(friends_data, columns)
        df.write.format("iceberg") \
            .mode("append") \
            .save(self.tableUtils.get_table())


