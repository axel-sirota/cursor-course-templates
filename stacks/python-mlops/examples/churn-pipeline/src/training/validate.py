import pandera as pa
from pandera import Column, DataFrameSchema
import pandas as pd

TRAINING_SCHEMA = DataFrameSchema({
    "customer_id": Column(str, nullable=False),
    "tenure_days": Column(int, pa.Check.ge(0)),
    "monthly_spend": Column(float, pa.Check.ge(0)),
    "support_tickets": Column(int, pa.Check.ge(0)),
    "churned": Column(int, pa.Check.isin([0, 1])),
})


def validate_training_data(df: pd.DataFrame) -> None:
    TRAINING_SCHEMA.validate(df)
