"""Unit tests for evaluation metrics and baseline auditor."""

import pytest
from pathlib import Path
import numpy as np
import pandas as pd
from src.metrics.evaluation import (
    calculate_wape,
    calculate_bias,
    calculate_mae,
    calculate_rmse,
    calculate_asymmetric_loss,
    evaluate_forecast,
)
from src.analysis.forecast_audit import BaselineAuditor


def test_calculate_wape_and_bias_known_values():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([80.0, 250.0, 270.0])
    # abs errors: |100-80|=20, |200-250|=50, |300-270|=30 -> sum = 100
    # signed errors: 20 + (-50) + 30 = 0
    # sum real: 600
    expected_wape = 100.0 / 600.0
    expected_bias = 0.0 / 600.0

    assert pytest.approx(calculate_wape(y_true, y_pred), abs=1e-6) == expected_wape
    assert pytest.approx(calculate_bias(y_true, y_pred), abs=1e-6) == expected_bias


def test_asymmetric_loss_penalization():
    y_true = np.array([100.0])
    # Underestimation: real (100) > pred (50) -> error = +50
    pred_under = np.array([50.0])
    # Overestimation: real (100) < pred (150) -> error = -50
    pred_over = np.array([150.0])

    loss_under = calculate_asymmetric_loss(y_true, pred_under, under_penalty=3.0, over_penalty=1.0)
    loss_over = calculate_asymmetric_loss(y_true, pred_over, under_penalty=3.0, over_penalty=1.0)

    # Underestimation loss should be exactly 3x overestimation loss
    assert pytest.approx(loss_under / loss_over, abs=1e-5) == 3.0


def test_baseline_auditor_execution():
    auditor = BaselineAuditor()
    m_glob = auditor.calculate_global_metrics()

    assert pytest.approx(m_glob["wape"], abs=1e-3) == 0.2084
    assert pytest.approx(m_glob["bias"], abs=1e-3) == 0.0655
    assert m_glob["n_obs"] == 1380

    mat_wape, mat_bias = auditor.calculate_cross_matrices()
    assert mat_wape.shape == (6, 4)
    assert mat_bias.shape == (6, 4)

    # Check CD_SUR subestimation
    assert mat_bias.loc["CD_SUR"].mean() > 0.30
    # Check CD_CENTRO sobreestimacion
    assert mat_bias.loc["CD_CENTRO"].mean() < -0.15


def test_baseline_summary_file_integrity():
    summary_path = Path("data/processed/baseline_metrics_summary.csv")
    assert summary_path.exists()
    df = pd.read_csv(summary_path)
    assert len(df) == 35  # 24 centro_horizonte + 6 centro + 4 horizonte + 1 global = 35
    assert "wape" in df.columns
    assert "bias" in df.columns
