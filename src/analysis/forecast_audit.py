"""Auditing and diagnostic module for baseline demand forecasting (Tarea 1)."""

from pathlib import Path
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.data.loader import load_processed_pronostico
from src.metrics.evaluation import evaluate_forecast

DEFAULT_FIGURES_DIR = Path("reports/figures/fase_02")
DEFAULT_PROCESSED_DIR = Path("data/processed")


class BaselineAuditor:
    """Performs deep audit on baseline forecast errors, bias patterns, and degradation."""

    def __init__(
        self,
        df: pd.DataFrame = None,
        figures_dir: Path = DEFAULT_FIGURES_DIR,
        processed_dir: Path = DEFAULT_PROCESSED_DIR,
    ):
        self.df = df if df is not None else load_processed_pronostico()
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = Path(processed_dir)

    def calculate_global_metrics(self) -> Dict[str, float]:
        """Calculates overarching baseline metrics."""
        return evaluate_forecast(self.df["unidades_reales"], self.df["unidades_pronosticadas"])

    def calculate_metrics_by_horizon(self) -> pd.DataFrame:
        """Calculates metrics grouped by forecast horizon (D+1, D+2, D+3, D+4)."""
        records = []
        for horizon, group in self.df.groupby("horizonte"):
            m = evaluate_forecast(group["unidades_reales"], group["unidades_pronosticadas"])
            m["horizonte"] = horizon
            records.append(m)
        df_res = pd.DataFrame(records).sort_values("horizonte").reset_index(drop=True)
        return df_res

    def calculate_metrics_by_centro(self) -> pd.DataFrame:
        """Calculates metrics grouped by distribution center."""
        records = []
        for centro, group in self.df.groupby("centro_distribucion"):
            m = evaluate_forecast(group["unidades_reales"], group["unidades_pronosticadas"])
            m["centro_distribucion"] = centro
            records.append(m)
        df_res = pd.DataFrame(records).sort_values("centro_distribucion").reset_index(drop=True)
        return df_res

    def calculate_cross_matrices(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Returns WAPE and Bias pivot matrices: (centro_distribucion x horizonte)."""
        records = []
        for (centro, horizon), group in self.df.groupby(["centro_distribucion", "horizonte"]):
            m = evaluate_forecast(group["unidades_reales"], group["unidades_pronosticadas"])
            m["centro_distribucion"] = centro
            m["horizonte"] = horizon
            records.append(m)
        df_res = pd.DataFrame(records)

        matrix_wape = df_res.pivot(index="centro_distribucion", columns="horizonte", values="wape")
        matrix_bias = df_res.pivot(index="centro_distribucion", columns="horizonte", values="bias")

        # Sort columns logically
        horizons_order = ["D+1", "D+2", "D+3", "D+4"]
        matrix_wape = matrix_wape[horizons_order]
        matrix_bias = matrix_bias[horizons_order]
        return matrix_wape, matrix_bias

    def export_baseline_summary(self) -> pd.DataFrame:
        """
        Creates and saves data/processed/baseline_metrics_summary.csv
        This serves as the official immutable benchmark for downstream modeling.
        """
        records = []
        # Center x Horizon level
        for (centro, horizon), group in self.df.groupby(["centro_distribucion", "horizonte"]):
            m = evaluate_forecast(group["unidades_reales"], group["unidades_pronosticadas"])
            m["nivel"] = "centro_horizonte"
            m["centro_distribucion"] = centro
            m["horizonte"] = horizon
            records.append(m)

        # Center level
        for centro, group in self.df.groupby("centro_distribucion"):
            m = evaluate_forecast(group["unidades_reales"], group["unidades_pronosticadas"])
            m["nivel"] = "centro"
            m["centro_distribucion"] = centro
            m["horizonte"] = "ALL"
            records.append(m)

        # Horizon level
        for horizon, group in self.df.groupby("horizonte"):
            m = evaluate_forecast(group["unidades_reales"], group["unidades_pronosticadas"])
            m["nivel"] = "horizonte"
            m["centro_distribucion"] = "ALL"
            m["horizonte"] = horizon
            records.append(m)

        # Global
        m_glob = self.calculate_global_metrics()
        m_glob["nivel"] = "global"
        m_glob["centro_distribucion"] = "ALL"
        m_glob["horizonte"] = "ALL"
        records.append(m_glob)

        df_summary = pd.DataFrame(records)
        cols_order = [
            "nivel",
            "centro_distribucion",
            "horizonte",
            "wape",
            "bias",
            "mae",
            "rmse",
            "asymmetric_loss",
            "total_real",
            "total_pred",
            "n_obs",
        ]
        df_summary = df_summary[cols_order]

        out_path = self.processed_dir / "baseline_metrics_summary.csv"
        df_summary.to_csv(out_path, index=False)
        return df_summary

    def generate_visualizations(self) -> None:
        """Generates and saves diagnostic plots for executive report."""
        sns.set_theme(style="whitegrid", palette="muted")
        matrix_wape, matrix_bias = self.calculate_cross_matrices()

        # 1. Heatmap WAPE
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            matrix_wape * 100,
            annot=True,
            fmt=".2f",
            cmap="YlOrRd",
            cbar_kws={"label": "WAPE (%)"},
            linewidths=0.5,
        )
        plt.title("Matriz de Error WAPE (%) por Centro y Horizonte", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Horizonte de Planificación", fontsize=11, fontweight="bold")
        plt.ylabel("Centro de Distribución", fontsize=11, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "heatmap_wape_centro_horizonte.png", dpi=300)
        plt.close()

        # 2. Heatmap Bias
        plt.figure(figsize=(8, 6))
        # Center diverging palette around 0
        vbound = max(abs(matrix_bias.values.min()), abs(matrix_bias.values.max())) * 100
        sns.heatmap(
            matrix_bias * 100,
            annot=True,
            fmt=".2f",
            cmap="vlag",
            center=0,
            vmin=-vbound,
            vmax=vbound,
            cbar_kws={"label": "Bias (%) (+ Subestima, - Sobreestima)"},
            linewidths=0.5,
        )
        plt.title("Matriz de Sesgo Estructural (Bias %) por Centro y Horizonte", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Horizonte de Planificación", fontsize=11, fontweight="bold")
        plt.ylabel("Centro de Distribución", fontsize=11, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "heatmap_bias_centro_horizonte.png", dpi=300)
        plt.close()

        # 3. Degradación Temporal WAPE
        df_hz = self.calculate_metrics_by_horizon()
        plt.figure(figsize=(8, 5))
        plt.plot(
            df_hz["horizonte"],
            df_hz["wape"] * 100,
            marker="o",
            linewidth=2.5,
            markersize=8,
            color="#d95f02",
            label="WAPE Global",
        )
        for _, row in df_hz.iterrows():
            plt.annotate(
                f"{row['wape']*100:.2f}%",
                (row["horizonte"], row["wape"] * 100),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontweight="bold",
                color="#b33d00",
            )
        plt.title("Degradación de Precisión Temporal del Pronóstico (WAPE %)", fontsize=13, fontweight="bold", pad=12)
        plt.xlabel("Horizonte de Planificación", fontsize=11, fontweight="bold")
        plt.ylabel("WAPE (%)", fontsize=11, fontweight="bold")
        plt.ylim(15, 26)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "degradacion_temporal_wape.png", dpi=300)
        plt.close()

        # 4. Distribución de Errores por Centro
        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=self.df,
            x="centro_distribucion",
            y="error",
            palette="Set2",
            showmeans=True,
            meanprops={"marker": "D", "markeredgecolor": "black", "markerfacecolor": "white"},
        )
        plt.axhline(0, color="red", linestyle="--", linewidth=1.2, label="Error Cero (Insustancial)")
        plt.title(
            "Distribución del Error de Demanda (Real - Pronóstico) por CD",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Centro de Distribución", fontsize=11, fontweight="bold")
        plt.ylabel("Error en Unidades Físicas (Real - Pronóstico)", fontsize=11, fontweight="bold")
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "distribucion_errores_por_centro.png", dpi=300)
        plt.close()

        print(f"[OK] 4 Gráficos de auditoría guardados en {self.figures_dir}")

    def run_full_audit(self) -> Dict:
        """Executes full diagnostic and exports all summary tables and figures."""
        global_m = self.calculate_global_metrics()
        df_hz = self.calculate_metrics_by_horizon()
        df_cd = self.calculate_metrics_by_centro()
        mat_wape, mat_bias = self.calculate_cross_matrices()
        summary_df = self.export_baseline_summary()
        self.generate_visualizations()

        return {
            "global": global_m,
            "by_horizon": df_hz,
            "by_centro": df_cd,
            "matrix_wape": mat_wape,
            "matrix_bias": mat_bias,
            "summary_df": summary_df,
        }


if __name__ == "__main__":
    auditor = BaselineAuditor()
    results = auditor.run_full_audit()
    print("\n--- RESUMEN GLOBAL ---")
    for k, v in results["global"].items():
        print(f"  {k}: {v}")
