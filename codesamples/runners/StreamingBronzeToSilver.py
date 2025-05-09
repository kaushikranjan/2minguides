from argparse import ArgumentParser

from src.catalogmanagement.IcebergReader import IcebergReader

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--intervalseconds", required=True,
                        help="Duration in seconds spark microbatches are going to get triggered")
    parser.add_argument("--namespace", required=True,
                        help="Namespace in Iceberg to write data to")
    parser.add_argument("--table", required=True,
                        help="Table in the namespace in Iceberg to write data into")
    parser.add_argument("--objectstore", required=True,
                        help="Object Store path, spark streaming will use for checkpointing")

    args = parser.parse_args()
    intervalseconds = int(args.intervalseconds)
    namespace = args.namespace
    table = args.table
    objectstore = args.objectstore

    reader = IcebergReader(namespace, table, objectstore)
    reader.read(intervalseconds)
