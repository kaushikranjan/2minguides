import time
from argparse import ArgumentParser

from src.catalogmanagement.IcebergWriter import IcebergWriter

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--waittime", required=True,
                        help="Time in seconds, thread will pause between each ingestion operation")
    parser.add_argument("--namespace", required=True,
                        help="Namespace in Iceberg to write data to")
    parser.add_argument("--table", required=True,
                        help="Table in the namespace in Iceberg to write data into")

    args = parser.parse_args()
    waittime = int(args.waittime)
    namespace = args.namespace
    table = args.table

    writer = IcebergWriter(namespace, table)
    writer.setup()
    while True:
        writer.append()
        time.sleep(waittime)
