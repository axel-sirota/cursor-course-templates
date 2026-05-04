# Spark Pipeline Starter Template

Use this scaffold when creating a new Spark pipeline from scratch.

## Directory Structure

```
{pipeline-name}/
  jobs/
    ingest.py           (Bronze: read source → write raw Delta)
    transform.py        (Silver: clean + type → write typed Delta)
    aggregate.py        (Gold: aggregate → write business table)
  tests/
    conftest.py         (SparkSession fixture)
    test_transform.py   (chispa assertions on transform logic)
    test_aggregate.py
    fixtures/
      sample_raw.csv    (small test input)
  configs/
    job.yml             (source paths, destination paths, options)
  requirements.txt      (pyspark, delta-spark, chispa, mlflow, ruff, mypy, pytest)
```

## Example `conftest.py`

```python
import pytest
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark() -> SparkSession:
    builder = (
        SparkSession.builder.master("local[*]")
        .appName("test")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()
```

## Example Transform Function

```python
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def clean_sales(spark: SparkSession, raw: DataFrame) -> DataFrame:
    return (
        raw
        .filter(F.col("amount").isNotNull())
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn("date", F.to_date(F.col("date_str"), "yyyy-MM-dd"))
        .drop("date_str")
    )
```

## Example Job Entrypoint

```python
import logging
import sys
import yaml
from pyspark.sql import SparkSession
from transform import clean_sales

logger = logging.getLogger(__name__)


def run(spark: SparkSession, config: dict) -> None:
    bronze_path = config["source"]["path"]
    silver_path = config["destination"]["path"]

    raw = spark.read.format("delta").load(bronze_path)
    silver = clean_sales(spark, raw)

    logger.info("Silver write: %d rows", silver.count())
    (
        silver.write
        .format("delta")
        .option("userMetadata", "silver-transform")
        .partitionBy(*config["options"]["partition_by"])
        .mode("overwrite")
        .save(silver_path)
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    spark = SparkSession.builder.appName("{pipeline-name}-transform").getOrCreate()
    with open("configs/job.yml") as f:
        config = yaml.safe_load(f)
    run(spark, config)
```

## Example chispa Test

```python
from chispa import assert_df_equality
from pyspark.sql.types import DoubleType, IntegerType, DateType, StructField, StructType
from jobs.transform import clean_sales
import datetime


def test_clean_sales_removes_null_amounts(spark):
    raw = spark.createDataFrame(
        [(1, 100.0, "2024-01-15"), (2, None, "2024-01-16"), (3, 50.0, "2024-01-17")],
        ["id", "amount", "date_str"],
    )
    result = clean_sales(spark, raw)
    assert result.count() == 2


def test_clean_sales_casts_amount_to_double(spark):
    raw = spark.createDataFrame(
        [(1, "99.99", "2024-01-15")],
        ["id", "amount", "date_str"],
    )
    result = clean_sales(spark, raw)
    assert result.schema["amount"].dataType == DoubleType()
```

## `requirements.txt`

```
pyspark>=3.5.0
delta-spark>=3.0.0
chispa>=0.9.0
mlflow>=2.10.0
ruff>=0.3.0
mypy>=1.8.0
pytest>=8.0.0
pytest-spark>=0.6.0
pyyaml>=6.0.0
```

## Version Compatibility

| PySpark | Delta Lake | Python |
|---------|-----------|--------|
| 3.5.x   | 3.2.x     | 3.9-3.11 |
| 3.4.x   | 2.4.x     | 3.9-3.11 |
| 3.3.x   | 2.2.x     | 3.8-3.10 |

> ⚠️ Delta Lake version must match PySpark version. Use delta-spark==3.2.0 with pyspark==3.5.x.
> Install: `pip install delta-spark==3.2.0 pyspark==3.5.3`
