"""
Unit tests for sales-pipeline transform functions.

Tests use chispa for DataFrame equality assertions. Each test:
- Creates a small input DataFrame with spark.createDataFrame
- Calls the transform function under test
- Asserts the result with assert_df_equality or targeted column-level checks

No Delta writes, no cluster, no file I/O — pure transform logic verification.
"""
import sys
import os

import pytest
from chispa import assert_df_equality
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DateType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

# Allow importing from jobs/ directory when running pytest from the pipeline root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jobs.transform import clean_sales, deduplicate_sales, enrich_sales


class TestCleanSales:
    """Tests for clean_sales() — null filtering, type casting, date parsing."""

    def test_removes_rows_with_null_amount(self, spark: SparkSession) -> None:
        """Rows with null amount must be dropped — they are invalid records."""
        raw = spark.createDataFrame(
            [
                (1, "West", "Widget", 100.0, "2024-01-15"),
                (2, "East", "Gadget", None, "2024-01-16"),
                (3, "West", "Widget", 50.0, "2024-01-17"),
            ],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        assert result.count() == 2
        ids = [row.id for row in result.select("id").collect()]
        assert 2 not in ids

    def test_casts_amount_to_double(self, spark: SparkSession) -> None:
        """amount column must be cast to DoubleType regardless of input type."""
        raw = spark.createDataFrame(
            [(1, "West", "Widget", "99.99", "2024-01-15")],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        assert result.schema["amount"].dataType == DoubleType()

    def test_parses_date_str_to_date(self, spark: SparkSession) -> None:
        """date_str (yyyy-MM-dd string) must be parsed into a DateType column named date."""
        raw = spark.createDataFrame(
            [(1, "West", "Widget", 100.0, "2024-03-22")],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        assert "date" in result.columns
        assert "date_str" not in result.columns
        assert result.schema["date"].dataType == DateType()

    def test_drops_date_str_column(self, spark: SparkSession) -> None:
        """The raw date_str column must not appear in the cleaned output."""
        raw = spark.createDataFrame(
            [(1, "West", "Widget", 100.0, "2024-01-15")],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        assert "date_str" not in result.columns

    def test_casts_id_to_integer(self, spark: SparkSession) -> None:
        """id must be cast to IntegerType for consistent Silver schema."""
        raw = spark.createDataFrame(
            [("1", "West", "Widget", 100.0, "2024-01-15")],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        assert result.schema["id"].dataType == IntegerType()

    def test_trims_region_whitespace(self, spark: SparkSession) -> None:
        """Leading/trailing whitespace in region must be stripped."""
        raw = spark.createDataFrame(
            [(1, "  West  ", "Widget", 100.0, "2024-01-15")],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        region_value = result.select("region").first()["region"]
        assert region_value == "West"

    def test_output_schema_matches_expected(self, spark: SparkSession) -> None:
        """Output DataFrame must have exactly the Silver columns in the correct order."""
        raw = spark.createDataFrame(
            [(1, "West", "Widget", 200.0, "2024-01-15")],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        assert result.columns == ["id", "region", "product", "amount", "date"]

    def test_full_equality_with_chispa(self, spark: SparkSession) -> None:
        """End-to-end row equality check using chispa with ignore_nullable=True."""
        import datetime

        raw = spark.createDataFrame(
            [
                (1, "West", "Widget", 100.0, "2024-01-15"),
                (2, "East", "Gadget", None, "2024-01-16"),
            ],
            ["id", "region", "product", "amount", "date_str"],
        )

        result = clean_sales(spark, raw)

        expected_schema = StructType(
            [
                StructField("id", IntegerType(), nullable=True),
                StructField("region", StringType(), nullable=True),
                StructField("product", StringType(), nullable=True),
                StructField("amount", DoubleType(), nullable=True),
                StructField("date", DateType(), nullable=True),
            ]
        )
        expected = spark.createDataFrame(
            [(1, "West", "Widget", 100.0, datetime.date(2024, 1, 15))],
            schema=expected_schema,
        )

        assert_df_equality(result, expected, ignore_nullable=True)


class TestDeduplicateSales:
    """Tests for deduplicate_sales() — keeps most recent record per id."""

    def test_removes_duplicate_ids(self, spark: SparkSession) -> None:
        """When the same id appears twice, only one row must remain."""
        import datetime

        schema = StructType(
            [
                StructField("id", IntegerType(), nullable=True),
                StructField("region", StringType(), nullable=True),
                StructField("product", StringType(), nullable=True),
                StructField("amount", DoubleType(), nullable=True),
                StructField("date", DateType(), nullable=True),
            ]
        )
        df = spark.createDataFrame(
            [
                (1, "West", "Widget", 100.0, datetime.date(2024, 1, 15)),
                (1, "West", "Widget", 150.0, datetime.date(2024, 1, 16)),
                (2, "East", "Gadget", 200.0, datetime.date(2024, 1, 15)),
            ],
            schema=schema,
        )

        result = deduplicate_sales(spark, df)

        assert result.count() == 2

    def test_keeps_most_recent_record(self, spark: SparkSession) -> None:
        """When duplicates exist, the row with the latest date must be kept."""
        import datetime

        schema = StructType(
            [
                StructField("id", IntegerType(), nullable=True),
                StructField("region", StringType(), nullable=True),
                StructField("product", StringType(), nullable=True),
                StructField("amount", DoubleType(), nullable=True),
                StructField("date", DateType(), nullable=True),
            ]
        )
        df = spark.createDataFrame(
            [
                (1, "West", "Widget", 100.0, datetime.date(2024, 1, 15)),
                (1, "West", "Widget", 150.0, datetime.date(2024, 1, 16)),
            ],
            schema=schema,
        )

        result = deduplicate_sales(spark, df)
        kept_amount = result.filter("id = 1").select("amount").first()["amount"]

        assert kept_amount == 150.0


class TestEnrichSales:
    """Tests for enrich_sales() — derived columns amount_category and year_month."""

    def test_adds_amount_category_low(self, spark: SparkSession) -> None:
        """Amount < 100 should produce category 'low'."""
        import datetime

        schema = StructType(
            [
                StructField("id", IntegerType(), nullable=True),
                StructField("region", StringType(), nullable=True),
                StructField("product", StringType(), nullable=True),
                StructField("amount", DoubleType(), nullable=True),
                StructField("date", DateType(), nullable=True),
            ]
        )
        df = spark.createDataFrame(
            [(1, "West", "Widget", 50.0, datetime.date(2024, 1, 15))],
            schema=schema,
        )

        result = enrich_sales(spark, df)
        category = result.select("amount_category").first()["amount_category"]

        assert category == "low"

    def test_adds_amount_category_medium(self, spark: SparkSession) -> None:
        """Amount between 100 and 999 should produce category 'medium'."""
        import datetime

        schema = StructType(
            [
                StructField("id", IntegerType(), nullable=True),
                StructField("region", StringType(), nullable=True),
                StructField("product", StringType(), nullable=True),
                StructField("amount", DoubleType(), nullable=True),
                StructField("date", DateType(), nullable=True),
            ]
        )
        df = spark.createDataFrame(
            [(2, "East", "Gadget", 500.0, datetime.date(2024, 1, 15))],
            schema=schema,
        )

        result = enrich_sales(spark, df)
        category = result.select("amount_category").first()["amount_category"]

        assert category == "medium"

    def test_adds_amount_category_high(self, spark: SparkSession) -> None:
        """Amount >= 1000 should produce category 'high'."""
        import datetime

        schema = StructType(
            [
                StructField("id", IntegerType(), nullable=True),
                StructField("region", StringType(), nullable=True),
                StructField("product", StringType(), nullable=True),
                StructField("amount", DoubleType(), nullable=True),
                StructField("date", DateType(), nullable=True),
            ]
        )
        df = spark.createDataFrame(
            [(3, "West", "Enterprise", 2000.0, datetime.date(2024, 1, 15))],
            schema=schema,
        )

        result = enrich_sales(spark, df)
        category = result.select("amount_category").first()["amount_category"]

        assert category == "high"

    def test_adds_year_month_column(self, spark: SparkSession) -> None:
        """year_month must be present and truncated to the first of the month."""
        import datetime

        schema = StructType(
            [
                StructField("id", IntegerType(), nullable=True),
                StructField("region", StringType(), nullable=True),
                StructField("product", StringType(), nullable=True),
                StructField("amount", DoubleType(), nullable=True),
                StructField("date", DateType(), nullable=True),
            ]
        )
        df = spark.createDataFrame(
            [(1, "West", "Widget", 100.0, datetime.date(2024, 3, 22))],
            schema=schema,
        )

        result = enrich_sales(spark, df)

        assert "year_month" in result.columns
        year_month = result.select("year_month").first()["year_month"]
        assert year_month == datetime.datetime(2024, 3, 1, 0, 0, 0)
