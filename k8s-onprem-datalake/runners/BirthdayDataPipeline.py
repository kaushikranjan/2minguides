import time
from argparse import ArgumentParser

from src.FriendTableHandler import FriendTableHandler
from src.ddl.CatalogUtils import CatalogUtils

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--database", required=True,
                        help="Name of the database to persist data to")

    args = parser.parse_args()
    database = args.database

    catalog_manager = CatalogUtils(database)
    friend_repository = FriendTableHandler(database)

    catalog_manager.create_namespace()
    friend_repository.create_friends_table()
    friend_repository.add_friends()

    time.sleep(600)
