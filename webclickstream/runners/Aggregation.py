from argparse import ArgumentParser
from src.utils.sparksessionutils import SparkSessionUtils
from src.transformation.pageviews import PageViewsTransformation
from src.transformation.clickevents import ClickEventsTransformation

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--aggregation_type", required=True,
                        help="Type of aggregation to perform (page_views or click_events)")
    
    args = parser.parse_args()
    aggregation_type = args.aggregation_type
    
    # Initialize Spark session
    spark = SparkSessionUtils().get_spark_session()
    
    if aggregation_type == "page_views":
        aggregation = PageViewsTransformation(spark)
        aggregation.aggregate()
    elif aggregation_type == "click_events":
        aggregation = ClickEventsTransformation(spark)
        aggregation.aggregate()
    else:
        raise ValueError(f"Unsupported aggregation type: {aggregation_type}")