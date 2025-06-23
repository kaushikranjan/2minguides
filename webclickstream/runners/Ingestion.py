from argparse import ArgumentParser
from src.ingestion.pageviews import PageViewsIngestion
from src.ingestion.clickevents import ClickEventsIngestion
from src.utils.sparksessionutils import SparkSessionUtils
import time

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--ingestion_type", required=True,
                        help="Type of ingestion to perform (page_views or click_events)")
    
    args = parser.parse_args()
    ingestion_type = args.ingestion_type
    
    # Initialize Spark session
    spark = SparkSessionUtils().get_spark_session()
    
    # Create ingestion instance based on type
    if ingestion_type == "click_events":
        ingestion = ClickEventsIngestion(spark)
        while True:
            ingestion.ingest_click_events()
            time.sleep(1)
    elif ingestion_type == "page_views":
        ingestion = PageViewsIngestion(spark)
        while True:
            ingestion.ingest_page_views()
            time.sleep(1)
    else:
        raise ValueError(f"Unsupported ingestion type: {ingestion_type}")