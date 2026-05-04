from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mlflow_tracking_uri: str = "sqlite:///mlruns.db"
    mlflow_experiment_name: str = "churn/gbm"
    model_name: str = "churn-30day"
    model_stage: str = "Production"
    min_auc_threshold: float = 0.75
    random_seed: int = 42


settings = Settings()
