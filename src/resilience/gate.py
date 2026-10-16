"""Resilience and cold start safety gate module (Tarea 4)."""

from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.data.loader import load_processed_demanda, load_processed_pronostico
from src.metrics.evaluation import evaluate_forecast
from src.models.corrector import ResidualDemandCorrector
from src.models.features import DemandFeaturePipeline

DEFAULT_FIGURES_DIR = Path("reports/figures/fase_05")
DEFAULT_PROCESSED_DIR = Path("data/processed")


@dataclass
class GateDecision:
    """Represents the operational outcome of evaluating history continuity."""
    centro_distribucion: str
    target_date: str
    is_eligible: bool
    continuous_days: int
    threshold_days: int
    mode: str  # "ADVANCED_MODEL" | "SAFE_FALLBACK"
    reason: str


class DataCoverageGate:
    """
    Evaluates temporal data coverage per distribution center and safely routes forecasting.
    Enforces the 45-day continuous history business rule without raising runtime exceptions.
    """

    def __init__(
        self,
        min_continuous_days: int = 45,
        figures_dir: Path = DEFAULT_FIGURES_DIR,
        processed_dir: Path = DEFAULT_PROCESSED_DIR,
    ):
        self.min_continuous_days = min_continuous_days
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = Path(processed_dir)

    def calculate_continuous_history_days(
        self,
        df_history: pd.DataFrame,
        target_date: Optional[Union[str, pd.Timestamp, date]] = None,
        date_column: str = "fecha_despacho",
    ) -> int:
        """
        Calculates the length of the continuous daily streak ending immediately before target_date.
        Detects missing dates (holes/gaps).
        """
        if df_history is None or len(df_history) == 0:
            return 0

        dates_series = pd.to_datetime(df_history[date_column]).drop_duplicates().sort_values()
        if len(dates_series) == 0:
            return 0

        if target_date is not None:
            t_date = pd.to_datetime(target_date)
            # Only consider dates strictly prior to target date
            dates_series = dates_series[dates_series < t_date]
            if len(dates_series) == 0:
                return 0

        dates_list = list(dates_series)
        streak = 1
        # Count backwards from the latest available date
        for i in range(len(dates_list) - 1, 0, -1):
            diff = (dates_list[i] - dates_list[i - 1]).days
            if diff == 1:
                streak += 1
            else:
                break

        return streak

    def evaluate_coverage(
        self,
        df_history: pd.DataFrame,
        centro_distribucion: str,
        target_date: Optional[Union[str, pd.Timestamp, date]] = None,
        date_column: str = "fecha_despacho",
    ) -> GateDecision:
        """Evaluates whether a CD meets the minimum 45-day continuous history requirement."""
        if df_history is None or len(df_history) == 0:
            return GateDecision(
                centro_distribucion=centro_distribucion,
                target_date=str(target_date),
                is_eligible=False,
                continuous_days=0,
                threshold_days=self.min_continuous_days,
                mode="SAFE_FALLBACK",
                reason="Historial nulo o vacío para el centro.",
            )

        # Filter by CD if present in history
        if "centro_distribucion" in df_history.columns:
            df_cd = df_history[df_history["centro_distribucion"] == centro_distribucion]
        else:
            df_cd = df_history

        streak = self.calculate_continuous_history_days(df_cd, target_date, date_column)
        target_str = str(target_date) if target_date else "LATEST"

        if streak >= self.min_continuous_days:
            return GateDecision(
                centro_distribucion=centro_distribucion,
                target_date=target_str,
                is_eligible=True,
                continuous_days=streak,
                threshold_days=self.min_continuous_days,
                mode="ADVANCED_MODEL",
                reason=f"Historial continuo suficiente ({streak} días >= {self.min_continuous_days} días).",
            )
        else:
            return GateDecision(
                centro_distribucion=centro_distribucion,
                target_date=target_str,
                is_eligible=False,
                continuous_days=streak,
                threshold_days=self.min_continuous_days,
                mode="SAFE_FALLBACK",
                reason=(
                    f"Cold Start / Historial insuficiente ({streak} días continuos < {self.min_continuous_days}). "
                    "Activando modo de resguardo seguro."
                ),
            )

    def dispatch_forecast(
        self,
        df_history: pd.DataFrame,
        centro_distribucion: str,
        base_forecast_units: float,
        target_date: Optional[Union[str, pd.Timestamp, date]] = None,
        model: Optional[ResidualDemandCorrector] = None,
        feature_vector: Optional[pd.DataFrame] = None,
    ) -> Dict:
        """
        Dispatches forecast securely:
        If eligible (>= 45 continuous days), routes through advanced ML corrector.
        If ineligible (< 45 continuous days or missing data), dispatches base forecast (fallback) safely.
        Never throws unhandled exceptions.
        """
        decision = self.evaluate_coverage(df_history, centro_distribucion, target_date)

        if decision.is_eligible and model is not None and feature_vector is not None:
            try:
                corrected = model.predict_corrected_demand(
                    feature_vector, pd.Series([base_forecast_units])
                )
                final_units = float(corrected[0])
                mode_used = "ADVANCED_MODEL"
                warning = None
            except Exception as e:
                # Emergency catch to ensure operational continuity
                final_units = float(base_forecast_units)
                mode_used = "SAFE_FALLBACK"
                warning = f"Excepción capturada en modelo complementario: {str(e)}. Fallback aplicado."
        else:
            final_units = float(base_forecast_units)
            mode_used = "SAFE_FALLBACK"
            warning = decision.reason

        return {
            "centro_distribucion": centro_distribucion,
            "target_date": decision.target_date,
            "forecast_units": final_units,
            "base_forecast_units": float(base_forecast_units),
            "mode_used": mode_used,
            "gate_decision": asdict(decision),
            "warning": warning,
        }

    def run_sensitivity_analysis(
        self,
        df_pronostico: Optional[pd.DataFrame] = None,
        df_demanda: Optional[pd.DataFrame] = None,
        thresholds: Tuple[int, ...] = (15, 20, 25, 30, 35, 40, 45, 50),
    ) -> pd.DataFrame:
        """
        Simulates model performance and statistical stability across different history depth thresholds.
        Saves results to data/processed/sensibilidad_gate_dias.csv.
        """
        if df_pronostico is None:
            df_pronostico = load_processed_pronostico()
        if df_demanda is None:
            df_demanda = load_processed_demanda()

        pipeline = DemandFeaturePipeline()
        df_feat = pipeline.fit_transform(df_pronostico, df_demanda)
        feature_cols = pipeline.feature_columns

        emission_dates = sorted(df_feat["fecha_emision"].unique())
        results = []

        for min_days in thresholds:
            if min_days >= len(emission_dates):
                continue
            y_true, y_pred_mod, y_pred_base = [], [], []

            for t_idx in range(min_days, len(emission_dates)):
                cur_date = emission_dates[t_idx]
                train_mask = df_feat["fecha_emision"] < cur_date
                test_mask = df_feat["fecha_emision"] == cur_date

                avail_train_dates = sorted(df_feat.loc[train_mask, "fecha_emision"].unique())
                # Simulate CD having exactly min_days history
                selected_train_dates = avail_train_dates[-min_days:]
                sub_train_mask = df_feat["fecha_emision"].isin(selected_train_dates)

                X_train = df_feat.loc[sub_train_mask, feature_cols]
                y_train = df_feat.loc[sub_train_mask, "residual"]

                X_test = df_feat.loc[test_mask, feature_cols]
                y_test = df_feat.loc[test_mask, "unidades_reales"]
                base_test = df_feat.loc[test_mask, "unidades_pronosticadas"]

                corrector = ResidualDemandCorrector()
                corrector.fit(X_train, y_train)
                pred_corr = corrector.predict_corrected_demand(X_test, base_test)

                y_true.extend(y_test.values)
                y_pred_mod.extend(pred_corr)
                y_pred_base.extend(base_test.values)

            y_t = np.array(y_true)
            y_m = np.array(y_pred_mod)
            y_b = np.array(y_pred_base)

            m_mod = evaluate_forecast(y_t, y_m)
            m_base = evaluate_forecast(y_t, y_b)

            relative_errors = np.abs(y_t - y_m) / (y_t + 1e-4)

            results.append(
                {
                    "umbral_dias_historia": min_days,
                    "semanas_equivalentes": round(min_days / 7.0, 2),
                    "wape_modelo": m_mod["wape"],
                    "wape_baseline": m_base["wape"],
                    "delta_wape_pp": (m_mod["wape"] - m_base["wape"]) * 100.0,
                    "bias_modelo": m_mod["bias"],
                    "dispersion_error_std": float(np.std(relative_errors)),
                    "pérdida_asimetrica_modelo": m_mod["asymmetric_loss"],
                    "n_evaluaciones": len(y_t),
                }
            )

        df_res = pd.DataFrame(results)
        out_path = self.processed_dir / "sensibilidad_gate_dias.csv"
        df_res.to_csv(out_path, index=False)
        return df_res

    def generate_visualizations(self) -> None:
        """Generates figures for Tarea 4."""
        sns.set_theme(style="whitegrid", palette="muted")
        df_res = self.run_sensitivity_analysis()

        # 1. Sensibilidad del WAPE vs Días de Historia
        plt.figure(figsize=(9, 5))
        plt.plot(
            df_res["umbral_dias_historia"],
            df_res["wape_modelo"] * 100,
            marker="o",
            linewidth=2.5,
            color="#27ae60",
            label="WAPE Modelo Corrector",
        )
        plt.axvline(
            45,
            color="#c0392b",
            linestyle="--",
            linewidth=1.8,
            label="Umbral de Resiliencia Calibrado (45 días)",
        )
        for _, row in df_res.iterrows():
            plt.annotate(
                f"{row['wape_modelo']*100:.2f}%",
                (row["umbral_dias_historia"], row["wape_modelo"] * 100),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=9,
                fontweight="bold",
            )
        plt.title(
            "Análisis de Sensibilidad: Estabilidad del WAPE según Profundidad de Historia",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Días Continuos de Historia en el CD", fontsize=11, fontweight="bold")
        plt.ylabel("WAPE (%)", fontsize=11, fontweight="bold")
        plt.ylim(5.5, 9.0)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "sensibilidad_umbral_dias_wape.png", dpi=300)
        plt.close()

        # 2. Diagrama de Flujo de Decision del Gate
        plt.figure(figsize=(10, 5))
        plt.text(
            0.5,
            0.85,
            "1. INGRESO DE REQUERIMIENTO DE PRONÓSTICO (CD, Fecha)",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#34495e", edgecolor="black"),
            fontweight="bold",
            color="white",
            fontsize=11,
        )
        plt.text(
            0.5,
            0.55,
            "2. INSPECCIÓN DE COBERTURA: ¿Días Continuos >= 45?",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.6", facecolor="#f39c12", edgecolor="black"),
            fontweight="bold",
            color="black",
            fontsize=11,
        )
        plt.text(
            0.2,
            0.2,
            "SÍ (>= 45 DÍAS)\nModo: ADVANCED_MODEL\nInferencia Modelo Corrector ML",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#2ecc71", edgecolor="black"),
            fontweight="bold",
            color="black",
            fontsize=10,
        )
        plt.text(
            0.8,
            0.2,
            "NO (< 45 DÍAS / GAPS)\nModo: SAFE_FALLBACK\nDespacho de Pronóstico Base (Sin Excepción)",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#e74c3c", edgecolor="black"),
            fontweight="bold",
            color="white",
            fontsize=10,
        )
        plt.annotate("", xy=(0.5, 0.65), xytext=(0.5, 0.77), arrowprops=dict(arrowstyle="->", lw=2))
        plt.annotate("", xy=(0.25, 0.3), xytext=(0.42, 0.48), arrowprops=dict(arrowstyle="->", lw=2))
        plt.annotate("", xy=(0.75, 0.3), xytext=(0.58, 0.48), arrowprops=dict(arrowstyle="->", lw=2))
        plt.axis("off")
        plt.title(
            "Arquitectura Lógica del Gate de Resiliencia Operativa",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.tight_layout()
        plt.savefig(self.figures_dir / "flujo_decision_resiliencia_gate.png", dpi=300)
        plt.close()

        print(f"[OK] 2 Gráficos de Fase 5 guardados en {self.figures_dir}")


if __name__ == "__main__":
    gate = DataCoverageGate()
    gate.generate_visualizations()
    df_sens = pd.read_csv("data/processed/sensibilidad_gate_dias.csv")
    print("\n--- ANÁLISIS DE SENSIBILIDAD DE UMBRALES (TAREA 4) ---")
    print(df_sens[["umbral_dias_historia", "semanas_equivalentes", "wape_modelo", "delta_wape_pp", "dispersion_error_std"]].to_string())
