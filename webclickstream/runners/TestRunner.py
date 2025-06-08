from argparse import ArgumentParser

from src.Sampler import Sampler

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--namespace", required=True,
                        help="Namespace in Iceberg to write data to")
    parser.add_argument("--table", required=True,
                        help="Table in the namespace in Iceberg to write data into")

    args = parser.parse_args()
    
    # Parse command line arguments for namespace and table
    # These arguments are required and will be used to specify the Iceberg table location
    namespace = args.namespace
    table = args.table


    # Create a Sampler instance with the provided namespace and table
    # This will be used to generate and write sample data to the Iceberg table
    writer = Sampler(namespace, table)
    writer.sample()