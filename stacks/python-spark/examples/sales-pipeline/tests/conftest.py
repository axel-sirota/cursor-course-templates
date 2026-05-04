"""
Shared pytest fixtures for sales-pipeline tests.

The SparkSession fixture is session-scoped — one SparkSession is created for the
entire test run and reused across all test files. This avoids the overhead of
starting and stopping Spark for each test.

Delta extensions are configured so that Delta Lake tables can be created in
integration tests via tmp_path.
"""
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """Create a local SparkSession with Delta Lake extensions for testing.

    Configuration:
    - master("local[2]"): two local threads — no cluster required
    - Delta extensions enabled: DeltaSparkSessionExtension + DeltaCatalog
    - Hive support disabled: keeps the session lightweight for unit tests
    - Adaptive Query Execution enabled: mimics production Spark behavior

    Returns:
        A configured SparkSession for the test session.
    """
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("sales-pipeline-test")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()
