"""Unit tests for DataCoverageGate and resilience mechanisms (Tarea 4)."""

import pytest
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
from src.resilience.gate import DataCoverageGate, GateDecision


@pytest.fixture
def gate():
    return DataCoverageGate(min_continuous_days=45)


def test_cold_start_under_threshold(gate):
    """Test CD with 15 days of continuous history: must route to SAFE_FALLBACK without exception."""
    start_date = date(2026, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(15)]
    df_hist = pd.DataFrame({
        "fecha_despacho": dates,
        "unidades_reales_total": [100.0] * 15,
        "centro_distribucion": ["CD_NUEVO"] * 15,
    })

    decision = gate.evaluate_coverage(df_hist, centro_distribucion="CD_NUEVO", target_date="2026-01-16")
    assert not decision.is_eligible
    assert decision.mode == "SAFE_FALLBACK"
    assert decision.continuous_days == 15

    # Safe dispatch verification
    result = gate.dispatch_forecast(
        df_hist,
        centro_distribucion="CD_NUEVO",
        base_forecast_units=250.0,
        target_date="2026-01-16",
    )
    assert result["mode_used"] == "SAFE_FALLBACK"
    assert result["forecast_units"] == 250.0
    assert "Cold Start" in result["warning"]


def test_boundary_conditions_44_vs_45_days(gate):
    """Test exact boundaries: 44 days (fallback) vs 45 days (advanced)."""
    start_date = date(2026, 1, 1)

    # 44 days
    df_44 = pd.DataFrame({
        "fecha_despacho": [start_date + timedelta(days=i) for i in range(44)],
        "unidades_reales_total": [100.0] * 44,
        "centro_distribucion": ["CD_TEST"] * 44,
    })
    dec_44 = gate.evaluate_coverage(df_44, "CD_TEST", target_date="2026-02-15")
    assert not dec_44.is_eligible
    assert dec_44.mode == "SAFE_FALLBACK"
    assert dec_44.continuous_days == 44

    # 45 days
    df_45 = pd.DataFrame({
        "fecha_despacho": [start_date + timedelta(days=i) for i in range(45)],
        "unidades_reales_total": [100.0] * 45,
        "centro_distribucion": ["CD_TEST"] * 45,
    })
    dec_45 = gate.evaluate_coverage(df_45, "CD_TEST", target_date="2026-02-16")
    assert dec_45.is_eligible
    assert dec_45.mode == "ADVANCED_MODEL"
    assert dec_45.continuous_days == 45


def test_history_with_gaps_continuity(gate):
    """Test that a gap in the timeline resets the continuous day counter."""
    # 30 days, then 5 missing days, then 20 days -> total 50 days of records, but streak is only 20
    d1 = [date(2026, 1, 1) + timedelta(days=i) for i in range(30)]
    d2 = [date(2026, 2, 5) + timedelta(days=i) for i in range(20)]
    all_dates = d1 + d2

    df_gap = pd.DataFrame({
        "fecha_despacho": all_dates,
        "unidades_reales_total": [100.0] * len(all_dates),
        "centro_distribucion": ["CD_GAP"] * len(all_dates),
    })

    streak = gate.calculate_continuous_history_days(df_gap, target_date="2026-02-26")
    assert streak == 20  # Only latest unbroken block counts

    decision = gate.evaluate_coverage(df_gap, "CD_GAP", target_date="2026-02-26")
    assert not decision.is_eligible
    assert decision.mode == "SAFE_FALLBACK"


def test_empty_corrupted_history_safe_fallback(gate):
    """Test that empty or corrupted history never crashes the application."""
    empty_df = pd.DataFrame()
    result = gate.dispatch_forecast(
        empty_df,
        centro_distribucion="CD_EMPTY",
        base_forecast_units=500.0,
    )
    assert result["mode_used"] == "SAFE_FALLBACK"
    assert result["forecast_units"] == 500.0

    none_res = gate.dispatch_forecast(
        None,
        centro_distribucion="CD_NONE",
        base_forecast_units=120.0,
    )
    assert none_res["mode_used"] == "SAFE_FALLBACK"
    assert none_res["forecast_units"] == 120.0


def test_sensitivity_artifact_exists():
    """Verify that sensitivity analysis table exists and has expected rows."""
    p = Path("data/processed/sensibilidad_gate_dias.csv")
    assert p.exists()
    df = pd.read_csv(p)
    assert len(df) >= 7
    assert "umbral_dias_historia" in df.columns
    assert "wape_modelo" in df.columns
