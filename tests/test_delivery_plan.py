"""Unit tests for delivery plan analysis, customer adherence, and capacity saturation."""

import pytest
from pathlib import Path
import pandas as pd
from src.analysis.delivery_plan import DeliveryPlanAnalyzer


@pytest.fixture
def analyzer():
    return DeliveryPlanAnalyzer()


def test_plan_bias_calculation(analyzer):
    bias_info = analyzer.calculate_plan_bias()

    assert bias_info["total_pedidos"] == 739
    assert bias_info["total_fuera_de_plan"] == 129
    assert pytest.approx(bias_info["pct_fuera_de_plan"], abs=1e-2) == 17.46
    # Commercial plan underestimates actual purchases by ~10.62%
    assert pytest.approx(bias_info["bias_unidades_pct"], abs=1e-2) == 10.62
    # Late orders outnumber early orders by ~3.45x
    assert bias_info["compras_retrasadas"] == 100
    assert bias_info["compras_adelantadas"] == 29
    assert pytest.approx(bias_info["late_to_early_ratio"], abs=1e-2) == 3.45


def test_fuera_de_plan_by_cd(analyzer):
    df_cd = analyzer.analyze_fuera_de_plan_by_cd()

    assert len(df_cd) == 6
    assert df_cd["total_pedidos"].sum() == 739
    # CD_NORTE has highest out-of-plan rate (~24.39%)
    cd_norte = df_cd[df_cd["centro_distribucion"] == "CD_NORTE"].iloc[0]
    assert pytest.approx(cd_norte["pct_fuera_de_plan"], abs=1e-2) == 24.39


def test_customer_adherence_artifact(analyzer):
    df_cust = analyzer.calculate_customer_adherence()

    assert len(df_cust) == 90  # 15 customers * 6 CDs = 90
    assert Path("data/processed/analisis_adhesion_clientes.csv").exists()
    assert "tasa_adhesion_pct" in df_cust.columns
    assert df_cust["tasa_adhesion_pct"].min() >= 0.0
    assert df_cust["tasa_adhesion_pct"].max() <= 100.0


def test_capacity_saturation_artifact(analyzer):
    df_sat = analyzer.analyze_capacity_saturation()

    assert len(df_sat) == 6
    assert Path("data/processed/saturacion_capacidad_cd.csv").exists()
    assert "pct_dias_saturados" in df_sat.columns
    # CD_NORTE has 6 saturated days (10%)
    cd_norte = df_sat[df_sat["centro_distribucion"] == "CD_NORTE"].iloc[0]
    assert cd_norte["dias_saturados"] == 6
    assert pytest.approx(cd_norte["pct_dias_saturados"], abs=1e-2) == 10.0
    assert cd_norte["exceso_unidades_total"] > 900.0
