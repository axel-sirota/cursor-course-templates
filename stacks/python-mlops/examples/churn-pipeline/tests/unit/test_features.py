import pandas as pd
import pytest

from src.training.features import compute_features


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "customer_id": ["c1", "c2"],
        "tenure_days": [365, 90],
        "monthly_spend": [50.0, 120.0],
        "support_tickets": [1, 5],
        "churned": [0, 1],
    })


def test_tenure_months_computed(sample_df: pd.DataFrame) -> None:
    result = compute_features(sample_df)
    assert "tenure_months" in result.columns
    assert result.loc[0, "tenure_months"] == pytest.approx(365 / 30)


def test_high_value_flag(sample_df: pd.DataFrame) -> None:
    result = compute_features(sample_df)
    assert result.loc[0, "high_value"] == 0
    assert result.loc[1, "high_value"] == 1


def test_tenure_days_dropped(sample_df: pd.DataFrame) -> None:
    result = compute_features(sample_df)
    assert "tenure_days" not in result.columns
