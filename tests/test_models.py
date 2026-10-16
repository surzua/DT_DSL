"""Unit tests for feature engineering, corrector model, and rolling backtest."""

import pytest
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from src.data.loader import load_processed_demanda, load_processed_pronostico
from src.models.features import DemandFeaturePipeline
from src.models.corrector import ResidualDemandCorrector
from src.models.backtest import RollingOriginBacktester


@pytest.fixture
def sample_data():
    df_pron = load_processed_pronostico()
    df_dem = load_processed_demanda()
    return df_pron, df_dem


def test_feature_pipeline_integrity(sample_data):
    df_pron, df_dem = sample_data
    pipeline = DemandFeaturePipeline()
    df_feat = pipeline.fit_transform(df_pron, df_dem)

    assert len(df_feat) == len(df_pron)
    assert not df_feat[pipeline.feature_columns].isnull().values.any()
    assert "es_martes" in pipeline.feature_columns
    assert "horizonte_num" in pipeline.feature_columns
    assert "mean_7d" in pipeline.feature_columns
    assert "ratio_base_to_mean7" in pipeline.feature_columns

    # Verify no leakage: fecha_despacho > fecha_emision
    assert (df_feat["fecha_despacho"] > df_feat["fecha_emision"]).all()


def test_residual_corrector_fit_predict():
    X = pd.DataFrame({
        "feat1": [1.0, 2.0, 3.0, 4.0],
        "feat2": [0.5, 1.0, 1.5, 2.0],
    })
    y_res = pd.Series([10.0, 20.0, 15.0, 25.0])
    base_pred = pd.Series([100.0, 100.0, 100.0, 100.0])

    corrector = ResidualDemandCorrector()
    corrector.fit(X, y_res)

    assert corrector.is_fitted
    pred_res = corrector.predict_residual(X)
    assert len(pred_res) == 4

    pred_corr = corrector.predict_corrected_demand(X, base_pred)
    assert len(pred_corr) == 4
    assert (pred_corr >= 0.0).all()

    df_imp = corrector.get_feature_importance()
    assert len(df_imp) == 2
    assert "importance" in df_imp.columns


def test_rolling_backtest_execution():
    backtester = RollingOriginBacktester(warmup_days=35)
    df_test = backtester.run_backtest()

    assert len(df_test) > 0
    assert "unidades_modelo_corregido" in df_test.columns
    assert (df_test["unidades_modelo_corregido"] >= 0.0).all()

    df_summary = backtester.generate_comparison_summary()
    assert Path("data/processed/backtest_results_comparison.csv").exists()

    glob = df_summary[df_summary["nivel"] == "global"].iloc[0]
    # WAPE must show significant reduction over baseline
    assert glob["wape_modelo"] < glob["wape_baseline"]
    assert glob["wape_modelo"] < 0.12  # Model WAPE is well below 12%
