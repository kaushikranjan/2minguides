from argparse import ArgumentParser
from src.utils.sparksessionutils import SparkSessionUtils
from src.transformation.pageviews import PageViewsTransformation
from src.transformation.clickevents import ClickEventsTransformation

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--transformation_type", required=True,
                        help="Type of transformation to perform (page_views or click_events)")
    
    args = parser.parse_args()
    transformation_type = args.transformation_type
    
    # Initialize Spark session
    spark = SparkSessionUtils().get_spark_session()
    
    # Create ingestion instance based on type
    # if transformation_type == "click_events":
    #     ingestion = ClickEventsIngestion(spark)
    #     while True:
    #         ingestion.ingest_click_events()
    #         time.sleep(10)
    if transformation_type == "page_views":
        transformation = PageViewsTransformation(spark)
        transformation.transform()
    elif transformation_type == "click_events":
        transformation = ClickEventsTransformation(spark)
        transformation.transform()
    else:
        raise ValueError(f"Unsupported ingestion type: {transformation_type}")