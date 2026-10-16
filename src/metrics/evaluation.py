"""Mathematical evaluation metrics for demand forecasting and logistics optimization."""

from typing import Dict, Union
import numpy as np
import pandas as pd


def calculate_wape(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
) -> float:
    """
    Weighted Absolute Percentage Error (WAPE):
    WAPE = sum(|real - pronostico|) / sum(|real|)
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)

    denom = np.sum(np.abs(y_t))
    if denom == 0.0:
        return 0.0
    return float(np.sum(np.abs(y_t - y_p)) / denom)


def calculate_bias(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
) -> float:
    """
    Forecast Bias:
    Bias = sum(real - pronostico) / sum(|real|)
    Positive (>0): Underestimation (real > forecast -> risk of stockout & spot freight).
    Negative (<0): Overestimation (real < forecast -> idle transport & holding cost).
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)

    denom = np.sum(np.abs(y_t))
    if denom == 0.0:
        return 0.0
    return float(np.sum(y_t - y_p) / denom)


def calculate_mae(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
) -> float:
    """Mean Absolute Error (MAE)."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_t - y_p)))


def calculate_rmse(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
) -> float:
    """Root Mean Squared Error (RMSE)."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_t - y_p) ** 2)))


def calculate_asymmetric_loss(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
    under_penalty: float = 2.5,
    over_penalty: float = 1.0,
) -> float:
    """
    Operational Asymmetric Cost Loss:
    Penalizes underestimation (real > forecast) more heavily than overestimation
    due to emergency spot transport hire and delivery SLA penalties.
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    error = y_t - y_p  # >0: underestimation, <0: overestimation

    loss = np.where(error >= 0, under_penalty * error, over_penalty * np.abs(error))
    denom = np.sum(np.abs(y_t))
    if denom == 0.0:
        return 0.0
    return float(np.sum(loss) / denom)


def evaluate_forecast(
    y_true: Union[np.ndarray, pd.Series],
    y_pred: Union[np.ndarray, pd.Series],
    under_penalty: float = 2.5,
    over_penalty: float = 1.0,
) -> Dict[str, float]:
    """Computes full set of evaluation metrics."""
    return {
        "wape": calculate_wape(y_true, y_pred),
        "bias": calculate_bias(y_true, y_pred),
        "mae": calculate_mae(y_true, y_pred),
        "rmse": calculate_rmse(y_true, y_pred),
        "asymmetric_loss": calculate_asymmetric_loss(
            y_true, y_pred, under_penalty=under_penalty, over_penalty=over_penalty
        ),
        "total_real": float(np.sum(y_true)),
        "total_pred": float(np.sum(y_pred)),
        "n_obs": int(len(y_true)),
    }
