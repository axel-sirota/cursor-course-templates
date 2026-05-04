from src.shared.config import settings


def evaluate_model(auc: float) -> None:
    if auc < settings.min_auc_threshold:
        raise ValueError(f"AUC {auc:.4f} below threshold {settings.min_auc_threshold}")
