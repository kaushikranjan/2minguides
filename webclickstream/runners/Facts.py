from argparse import ArgumentParser
from src.facts.productfacts import ProductFacts
from src.utils.sparksessionutils import SparkSessionUtils

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--facts_type", required=True,
                        help="Type of facts to perform (product_metrics)")

    args = parser.parse_args()
    facts_type = args.facts_type
    
    # Initialize Spark session
    spark = SparkSessionUtils().get_spark_session()
    
    if facts_type == "page_views":
        product_metrics = ProductFacts(spark)
        product_metrics.create_product_facts_from_page_view()
    elif facts_type == "click_events":
        product_metrics = ProductFacts(spark)
        product_metrics.create_product_facts_from_click_events()
    else:
        raise ValueError(f"Unsupported facts type: {facts_type}")