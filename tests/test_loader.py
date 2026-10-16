"""Unit tests for data loader, contracts, and schema validation."""

import pytest
import pandas as pd
from pathlib import Path

from src.data.loader import (
    DataLoader,
    load_processed_demanda,
    load_processed_pronostico,
    load_processed_capacidad,
    load_processed_plan_entrega,
)
from src.data.schemas import EXPECTED_CENTROS


@pytest.fixture
def loader():
    return DataLoader()


def test_referential_integrity(loader):
    """Test that all 4 raw datasets have all 6 expected distribution centers."""
    summary = loader.validate_referential_integrity()
    for name, centros in summary.items():
        assert centros == EXPECTED_CENTROS, f"Fallo en centros de {name}"


def test_aggregation_conservation_of_units(loader):
    """Test that central aggregation perfectly preserves total units delivered."""
    df_raw = loader.load_pedidos_historicos()
    df_agg = loader.aggregate_demanda_real(df_raw)

    total_raw_units = df_raw["unidades_reales"].sum()
    total_agg_units = df_agg["unidades_reales_total"].sum()

    assert pytest.approx(total_raw_units, rel=1e-5) == total_agg_units
    # Exactly 60 days * 6 distribution centers = 360 rows
    assert len(df_agg) == 360
    assert not df_agg.isnull().values.any(), "Existen valores nulos en demanda agregada"


def test_pronostico_merge_coverage(loader):
    """Test that all 1380 forecast points match real delivery points without nulls."""
    df_eval = loader.build_pronostico_base_evaluacion()
    assert len(df_eval) == 1380
    assert not df_eval["unidades_reales"].isnull().any()
    assert not df_eval["unidades_pronosticadas"].isnull().any()
    assert (df_eval["error"] == df_eval["unidades_reales"] - df_eval["unidades_pronosticadas"]).all()


def test_parquet_persistence_and_loading(loader, tmp_path):
    """Test that the pipeline saves and reads parquets cleanly."""
    loader_tmp = DataLoader(processed_dir=tmp_path)
    demanda, pronostico = loader_tmp.run_pipeline()

    assert (tmp_path / "demanda_real_agregada.parquet").exists()
    assert (tmp_path / "pronostico_base_limpio.parquet").exists()
    assert (tmp_path / "capacidad_logistica_limpia.parquet").exists()
    assert (tmp_path / "plan_entrega_limpio.parquet").exists()

    df_loaded = pd.read_parquet(tmp_path / "demanda_real_agregada.parquet")
    assert len(df_loaded) == len(demanda)
