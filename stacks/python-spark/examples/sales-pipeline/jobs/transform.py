"""
Silver transformation job: reads Bronze Delta, cleans and types the data, writes to Silver.

Transform functions are pure — they take a SparkSession and a DataFrame and return a
DataFrame. No Spark infrastructure is created inside transform functions.
"""
import logging
import sys

import yaml
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DateType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

logger = logging.getLogger(__name__)

SILVER_SCHEMA = StructType(
    [
        StructField("id", IntegerType(), nullable=False),
        StructField("region", StringType(), nullable=True),
        StructField("product", StringType(), nullable=True),
        StructField("amount", DoubleType(), nullable=True),
        StructField("date", DateType(), nullable=True),
    ]
)


def clean_sales(spark: SparkSession, raw: DataFrame) -> DataFrame:
    """Clean and type raw Bronze sales data into a Silver-quality DataFrame.

    Transformations applied:
    - Filter rows where `amount` is null (invalid records)
    - Cast `amount` to double
    - Parse `date_str` (yyyy-MM-dd) into a proper DateType column `date`
    - Drop the raw `date_str` column
    - Cast `id` to integer

    Args:
        spark: Active SparkSession (injected, not created here).
        raw: Raw Bronze DataFrame with inferred types from CSV.

    Returns:
        Cleaned Silver DataFrame conforming to SILVER_SCHEMA.
    """
    cleaned: DataFrame = (
        raw
        .filter(F.col("amount").isNotNull())
        .withColumn("id", F.col("id").cast(IntegerType()))
        .withColumn("amount", F.col("amount").cast(DoubleType()))
        .withColumn("date", F.to_date(F.col("date_str"), "yyyy-MM-dd"))
        .withColumn("region", F.trim(F.col("region")))
        .withColumn("product", F.trim(F.col("product")))
        .drop("date_str")
        .select("id", "region", "product", "amount", "date")
    )
    return cleaned


def deduplicate_sales(spark: SparkSession, df: DataFrame) -> DataFrame:
    """Remove duplicate rows, keeping the most recent record per id.

    Uses window function to rank by date descending and keep rank=1.

    Args:
        spark: Active SparkSession (injected).
        df: DataFrame that may contain duplicate ids.

    Returns:
        Deduplicated DataFrame with one row per id.
    """
    from pyspark.sql import Window

    window = Window.partitionBy("id").orderBy(F.col("date").desc())

    deduplicated: DataFrame = (
        df
        .withColumn("_rank", F.row_number().over(window))
        .filter(F.col("_rank") == 1)
        .drop("_rank")
    )
    return deduplicated


def enrich_sales(spark: SparkSession, df: DataFrame) -> DataFrame:
    """Add derived columns to enrich the Silver dataset.

    Additions:
    - `amount_category`: "low" (< 100), "medium" (100–999), "high" (>= 1000)
    - `year_month`: date truncated to first of the month (for partitioning)

    Args:
        spark: Active SparkSession (injected).
        df: Cleaned and deduplicated DataFrame.

    Returns:
        Enriched DataFrame with additional derived columns.
    """
    enriched: DataFrame = (
        df
        .withColumn(
            "amount_category",
            F.when(F.col("amount") < 100, F.lit("low"))
            .when(F.col("amount") < 1000, F.lit("medium"))
            .otherwise(F.lit("high")),
        )
        .withColumn("year_month", F.date_trunc("month", F.col("date")))
    )
    return enriched


def run(spark: SparkSession, config: dict) -> None:
    """Orchestrate the full Bronze → Silver transformation pipeline.

    Args:
        spark: Active SparkSession.
        config: Parsed job.yml config dict.
    """
    bronze_path: str = config["source"]["path"]
    silver_path: str = config["destination"]["path"]
    partition_cols: list = config["options"].get("partition_by", ["date"])

    logger.info("Reading Bronze from %s", bronze_path)
    raw: DataFrame = spark.read.format("delta").load(bronze_path)

    cleaned = clean_sales(spark, raw)
    deduped = deduplicate_sales(spark, cleaned)
    enriched = enrich_sales(spark, deduped)

    row_count = enriched.count()
    logger.info("Silver write: %d rows", row_count)

    (
        enriched.write
        .format("delta")
        .option("mergeSchema", "false")
        .option("userMetadata", "silver-transform")
        .partitionBy(*partition_cols)
        .mode("overwrite")
        .save(silver_path)
    )

    logger.info("Silver write complete: %d rows written to %s", row_count, silver_path)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/job.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    spark = (
        SparkSession.builder
        .appName(config["job"]["name"])
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )

    run(spark, config)
    spark.stop()
