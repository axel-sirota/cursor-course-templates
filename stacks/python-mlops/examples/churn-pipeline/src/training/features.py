import pandas as pd


def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        tenure_months=df["tenure_days"] / 30,
        high_value=(df["monthly_spend"] > 100).astype(int),
    ).drop(columns=["tenure_days"])
