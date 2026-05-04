"""
Bronze ingestion job: reads raw CSV sales data and writes to Delta Lake (Bronze layer).

This is the entrypoint for the ingest stage. No transformations are applied — raw data
is written as-is to preserve the source record. Schema inference is used (Bronze layer).
"""
import logging
import sys
from typing import Optional

import yaml
from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)


def ingest(
    spark: SparkSession,
    source_path: str,
    destination_path: str,
    source_format: str = "csv",
) -> DataFrame:
    """Read raw source data and return the ingested DataFrame.

    No transformations are applied. The raw record is preserved exactly as received.

    Args:
        spark: Active SparkSession (injected by caller).
        source_path: Path to the source data file or directory.
        destination_path: Delta Lake path to write Bronze output.
        source_format: Source format — "csv", "parquet", or "json". Default: "csv".

    Returns:
        The ingested DataFrame (before write).
    """
    logger.info("Reading source from %s (format=%s)", source_path, source_format)

    if source_format == "csv":
        raw: DataFrame = (
            spark.read
            .option("header", "true")
            .option("inferSchema", "true")
            .csv(source_path)
        )
    elif source_format == "parquet":
        raw = spark.read.parquet(source_path)
    elif source_format == "json":
        raw = spark.read.json(source_path)
    else:
        raise ValueError(f"Unsupported source format: {source_format}")

    row_count = raw.count()
    logger.info("Bronze ingest: %d rows read from source", row_count)

    (
        raw.write
        .format("delta")
        .option("mergeSchema", "true")
        .option("userMetadata", f"bronze-ingest-{source_path}")
        .mode("append")
        .save(destination_path)
    )

    logger.info("Bronze write complete: %d rows written to %s", row_count, destination_path)
    return raw


def run(spark: SparkSession, config: dict) -> None:
    """Orchestrate the ingest job using config values.

    Args:
        spark: Active SparkSession.
        config: Parsed job.yml config dict.
    """
    source_path: str = config["source"]["path"]
    source_format: str = config["source"].get("format", "csv")
    destination_path: str = config["destination"]["path"]

    ingest(spark, source_path, destination_path, source_format)


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
