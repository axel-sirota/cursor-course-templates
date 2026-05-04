import os
import pytest


@pytest.fixture(autouse=True, scope="session")
def mlflow_test_tracking(tmp_path_factory):  # type: ignore[no-untyped-def]
    db = tmp_path_factory.mktemp("mlruns") / "test.db"
    os.environ["MLFLOW_TRACKING_URI"] = f"sqlite:///{db}"
    yield
    os.environ.pop("MLFLOW_TRACKING_URI", None)
