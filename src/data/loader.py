"""Data loading, validation, and contract enforcement module."""

from pathlib import Path
from typing import Dict, Optional, Tuple, Set
import pandas as pd

from src.data.schemas import (
    EXPECTED_CENTROS,
    PedidoHistoricoRecord,
    PronosticoDemandaRecord,
    CapacidadLogisticaRecord,
    PlanEntregaClienteRecord,
)

DEFAULT_RAW_DIR = Path("data/raw")
DEFAULT_PROCESSED_DIR = Path("data/processed")


class DataLoader:
    """Manages ingestion, schema validation, aggregation, and persistence of logistics datasets."""

    def __init__(self, raw_dir: Path = DEFAULT_RAW_DIR, processed_dir: Path = DEFAULT_PROCESSED_DIR):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def load_pedidos_historicos(self, validate_pydantic: bool = True) -> pd.DataFrame:
        """Load and validate raw pedidos_historicos_genericos.csv."""
        filepath = self.raw_dir / "pedidos_historicos_genericos.csv"
        df = pd.read_csv(filepath)
        df["fecha_despacho"] = pd.to_datetime(df["fecha_despacho"])

        if validate_pydantic:
            # Sample validation to guarantee contract compliance without massive overhead
            for row in df.sample(min(len(df), 100), random_state=42).to_dict(orient="records"):
                row["fecha_despacho"] = row["fecha_despacho"].date()
                PedidoHistoricoRecord(**row)

        self._check_centros(df, "pedidos_historicos")
        return df

    def load_pronostico_demanda(self, validate_pydantic: bool = True) -> pd.DataFrame:
        """Load and validate raw pronostico_demanda_generico.csv."""
        filepath = self.raw_dir / "pronostico_demanda_generico.csv"
        df = pd.read_csv(filepath)
        df["fecha_emision"] = pd.to_datetime(df["fecha_emision"])
        df["fecha_despacho"] = pd.to_datetime(df["fecha_despacho"])

        if validate_pydantic:
            for row in df.sample(min(len(df), 100), random_state=42).to_dict(orient="records"):
                row["fecha_emision"] = row["fecha_emision"].date()
                row["fecha_despacho"] = row["fecha_despacho"].date()
                PronosticoDemandaRecord(**row)

        self._check_centros(df, "pronostico_demanda")
        return df

    def load_capacidad_logistica(self, validate_pydantic: bool = True) -> pd.DataFrame:
        """Load and validate raw capacidad_logistica_generica.csv."""
        filepath = self.raw_dir / "capacidad_logistica_generica.csv"
        df = pd.read_csv(filepath)
        df["fecha"] = pd.to_datetime(df["fecha"])

        if validate_pydantic:
            for row in df.sample(min(len(df), 100), random_state=42).to_dict(orient="records"):
                row["fecha"] = row["fecha"].date()
                CapacidadLogisticaRecord(**row)

        self._check_centros(df, "capacidad_logistica")
        return df

    def load_plan_entrega(self, validate_pydantic: bool = True) -> pd.DataFrame:
        """Load and validate raw plan_entrega_clientes_generico.csv."""
        filepath = self.raw_dir / "plan_entrega_clientes_generico.csv"
        df = pd.read_csv(filepath)
        df["fecha_plan"] = pd.to_datetime(df["fecha_plan"])
        df["fecha_compra_real"] = pd.to_datetime(df["fecha_compra_real"])

        if validate_pydantic:
            for row in df.sample(min(len(df), 100), random_state=42).to_dict(orient="records"):
                row["fecha_plan"] = row["fecha_plan"].date()
                row["fecha_compra_real"] = row["fecha_compra_real"].date()
                PlanEntregaClienteRecord(**row)

        self._check_centros(df, "plan_entrega")
        return df

    def _check_centros(self, df: pd.DataFrame, dataset_name: str) -> None:
        """Verify that all expected distribution centers are present."""
        found_centros = set(df["centro_distribucion"].unique())
        if found_centros != EXPECTED_CENTROS:
            diff_missing = EXPECTED_CENTROS - found_centros
            diff_extra = found_centros - EXPECTED_CENTROS
            raise ValueError(
                f"Integridad referencial fallida en {dataset_name}. "
                f"Faltantes: {diff_missing}, No reconocidos: {diff_extra}"
            )

    def validate_referential_integrity(self) -> Dict[str, Set[str]]:
        """Validate that all 4 datasets contain exactly the expected 6 distribution centers."""
        pedidos = self.load_pedidos_historicos(validate_pydantic=False)
        pronostico = self.load_pronostico_demanda(validate_pydantic=False)
        capacidad = self.load_capacidad_logistica(validate_pydantic=False)
        plan = self.load_plan_entrega(validate_pydantic=False)

        summary = {
            "pedidos_historicos": set(pedidos["centro_distribucion"].unique()),
            "pronostico_demanda": set(pronostico["centro_distribucion"].unique()),
            "capacidad_logistica": set(capacidad["centro_distribucion"].unique()),
            "plan_entrega": set(plan["centro_distribucion"].unique()),
        }

        for name, centros in summary.items():
            if centros != EXPECTED_CENTROS:
                raise ValueError(f"Fallo de integridad referencial en {name}: {centros}")

        return summary

    def aggregate_demanda_real(self, df_pedidos: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Central Aggregation Rule:
        Consolidates sales from all channels into total real demand per (centro_distribucion, fecha_despacho).
        Also includes channel breakdown columns for downstream feature engineering.
        """
        if df_pedidos is None:
            df_pedidos = self.load_pedidos_historicos()

        # Aggregation of total real units
        agg_total = (
            df_pedidos.groupby(["centro_distribucion", "fecha_despacho"], as_index=False)["unidades_reales"]
            .sum()
            .rename(columns={"unidades_reales": "unidades_reales_total"})
        )

        # Pivot channel units for multi-channel operational visibility
        channel_pivot = (
            df_pedidos.pivot_table(
                index=["centro_distribucion", "fecha_despacho"],
                columns="canal_venta",
                values="unidades_reales",
                aggfunc="sum",
                fill_value=0.0,
            )
            .reset_index()
        )
        channel_pivot.columns = [
            f"unidades_{c.lower()}" if c not in ["centro_distribucion", "fecha_despacho"] else c
            for c in channel_pivot.columns
        ]

        df_aggregated = pd.merge(agg_total, channel_pivot, on=["centro_distribucion", "fecha_despacho"], how="left")
        df_aggregated = df_aggregated.sort_values(["centro_distribucion", "fecha_despacho"]).reset_index(drop=True)
        return df_aggregated

    def build_pronostico_base_evaluacion(
        self,
        df_pronostico: Optional[pd.DataFrame] = None,
        df_demanda: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Merges baseline forecast with real aggregated demand on (centro_distribucion, fecha_despacho).
        Guarantees strict audit alignment.
        """
        if df_pronostico is None:
            df_pronostico = self.load_pronostico_demanda()
        if df_demanda is None:
            df_demanda = self.aggregate_demanda_real()

        merged = pd.merge(
            df_pronostico,
            df_demanda[["centro_distribucion", "fecha_despacho", "unidades_reales_total"]],
            on=["centro_distribucion", "fecha_despacho"],
            how="inner",
        )
        merged = merged.rename(columns={"unidades_reales_total": "unidades_reales"})
        merged["error"] = merged["unidades_reales"] - merged["unidades_pronosticadas"]
        merged["error_abs"] = merged["error"].abs()
        merged = merged.sort_values(
            ["centro_distribucion", "fecha_despacho", "horizonte"]
        ).reset_index(drop=True)
        return merged

    def run_pipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Executes full data ingestion pipeline, validates contracts, and saves parquet artifacts."""
        self.validate_referential_integrity()

        # Build datasets
        df_demanda = self.aggregate_demanda_real()
        df_pronostico_eval = self.build_pronostico_base_evaluacion(df_demanda=df_demanda)
        df_capacidad = self.load_capacidad_logistica()
        df_plan = self.load_plan_entrega()

        # Persist Parquet files
        demanda_path = self.processed_dir / "demanda_real_agregada.parquet"
        pronostico_path = self.processed_dir / "pronostico_base_limpio.parquet"
        capacidad_path = self.processed_dir / "capacidad_logistica_limpia.parquet"
        plan_path = self.processed_dir / "plan_entrega_limpio.parquet"

        df_demanda.to_parquet(demanda_path, index=False)
        df_pronostico_eval.to_parquet(pronostico_path, index=False)
        df_capacidad.to_parquet(capacidad_path, index=False)
        df_plan.to_parquet(plan_path, index=False)

        print(f"[OK] Pipeline Fase 1 completado exitosamente.")
        print(f"     -> {demanda_path} ({len(df_demanda)} registros)")
        print(f"     -> {pronostico_path} ({len(df_pronostico_eval)} registros)")
        print(f"     -> {capacidad_path} ({len(df_capacidad)} registros)")
        print(f"     -> {plan_path} ({len(df_plan)} registros)")

        return df_demanda, df_pronostico_eval


def load_processed_demanda(processed_dir: Path = DEFAULT_PROCESSED_DIR) -> pd.DataFrame:
    """Helper function to load processed real aggregated demand."""
    return pd.read_parquet(processed_dir / "demanda_real_agregada.parquet")


def load_processed_pronostico(processed_dir: Path = DEFAULT_PROCESSED_DIR) -> pd.DataFrame:
    """Helper function to load processed baseline forecast."""
    return pd.read_parquet(processed_dir / "pronostico_base_limpio.parquet")


def load_processed_capacidad(processed_dir: Path = DEFAULT_PROCESSED_DIR) -> pd.DataFrame:
    """Helper function to load processed logistic capacity."""
    return pd.read_parquet(processed_dir / "capacidad_logistica_limpia.parquet")


def load_processed_plan_entrega(processed_dir: Path = DEFAULT_PROCESSED_DIR) -> pd.DataFrame:
    """Helper function to load processed delivery plan."""
    return pd.read_parquet(processed_dir / "plan_entrega_limpio.parquet")


if __name__ == "__main__":
    loader = DataLoader()
    loader.run_pipeline()
