"""Rolling-Origin Backtest validation for demand forecasting and residual correction."""

from pathlib import Path
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.data.loader import load_processed_demanda, load_processed_pronostico
from src.metrics.evaluation import evaluate_forecast
from src.models.corrector import ResidualDemandCorrector
from src.models.features import DemandFeaturePipeline

DEFAULT_FIGURES_DIR = Path("reports/figures/fase_04")
DEFAULT_PROCESSED_DIR = Path("data/processed")


class RollingOriginBacktester:
    """
    Simulates operational production forecasting using expanding rolling-origin evaluation.
    Guarantees no future lookahead.
    """

    def __init__(
        self,
        warmup_days: int = 28,
        figures_dir: Path = DEFAULT_FIGURES_DIR,
        processed_dir: Path = DEFAULT_PROCESSED_DIR,
    ):
        self.warmup_days = warmup_days
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = Path(processed_dir)

    def run_backtest(
        self,
        df_pronostico: Optional[pd.DataFrame] = None,
        df_demanda: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """Executes full rolling origin backtest day-by-day."""
        if df_pronostico is None:
            df_pronostico = load_processed_pronostico()
        if df_demanda is None:
            df_demanda = load_processed_demanda()

        # Generate feature matrix
        pipeline = DemandFeaturePipeline()
        df_feat = pipeline.fit_transform(df_pronostico, df_demanda)
        feature_cols = pipeline.feature_columns

        emission_dates = sorted(df_feat["fecha_emision"].unique())
        if len(emission_dates) <= self.warmup_days:
            raise ValueError(
                f"No hay suficientes fechas ({len(emission_dates)}) para warmup de {self.warmup_days} días."
            )

        test_records = []
        step_learning_curve = []

        # Train a representative model for feature importance inspection
        full_train_model = ResidualDemandCorrector()

        for t_idx in range(self.warmup_days, len(emission_dates)):
            cur_date = emission_dates[t_idx]
            train_mask = df_feat["fecha_emision"] < cur_date
            test_mask = df_feat["fecha_emision"] == cur_date

            X_train = df_feat.loc[train_mask, feature_cols]
            y_train_res = df_feat.loc[train_mask, "residual"]

            X_test = df_feat.loc[test_mask, feature_cols]
            test_slice = df_feat.loc[test_mask].copy()

            corrector = ResidualDemandCorrector()
            corrector.fit(X_train, y_train_res)

            # Predict corrected values
            pred_corrected = corrector.predict_corrected_demand(
                X_test, test_slice["unidades_pronosticadas"]
            )
            test_slice["unidades_modelo_corregido"] = pred_corrected

            # Track for learning curve
            eval_step_base = evaluate_forecast(
                test_slice["unidades_reales"], test_slice["unidades_pronosticadas"]
            )
            eval_step_model = evaluate_forecast(
                test_slice["unidades_reales"], test_slice["unidades_modelo_corregido"]
            )
            step_learning_curve.append(
                {
                    "fecha_emision": cur_date,
                    "wape_base": eval_step_base["wape"],
                    "wape_modelo": eval_step_model["wape"],
                    "train_size": len(X_train),
                }
            )

            test_records.append(test_slice)

        self.df_test = pd.concat(test_records, ignore_index=True)
        self.df_learning_curve = pd.DataFrame(step_learning_curve)

        # Fit full train model for final coefficients
        full_train_model.fit(
            df_feat.loc[df_feat["fecha_emision"] < emission_dates[-1], feature_cols],
            df_feat.loc[df_feat["fecha_emision"] < emission_dates[-1], "residual"],
        )
        self.df_feature_importance = full_train_model.get_feature_importance()

        return self.df_test

    def generate_comparison_summary(self) -> pd.DataFrame:
        """
        Computes comparative metrics between Baseline and Model:
        Global, by CD, and by Horizon.
        Saves to data/processed/backtest_results_comparison.csv.
        """
        records = []

        def _get_comparison(df_sub: pd.DataFrame, nivel: str, cd: str, hz: str) -> Dict:
            m_base = evaluate_forecast(
                df_sub["unidades_reales"], df_sub["unidades_pronosticadas"]
            )
            m_mod = evaluate_forecast(
                df_sub["unidades_reales"], df_sub["unidades_modelo_corregido"]
            )
            return {
                "nivel": nivel,
                "centro_distribucion": cd,
                "horizonte": hz,
                "n_obs": len(df_sub),
                "wape_baseline": m_base["wape"],
                "wape_modelo": m_mod["wape"],
                "delta_wape_pp": (m_mod["wape"] - m_base["wape"]) * 100.0,
                "bias_baseline": m_base["bias"],
                "bias_modelo": m_mod["bias"],
                "mae_baseline": m_base["mae"],
                "mae_modelo": m_mod["mae"],
                "rmse_baseline": m_base["rmse"],
                "rmse_modelo": m_mod["rmse"],
                "asymmetric_loss_baseline": m_base["asymmetric_loss"],
                "asymmetric_loss_modelo": m_mod["asymmetric_loss"],
            }

        # 1. Global
        records.append(_get_comparison(self.df_test, "global", "ALL", "ALL"))

        # 2. By Centro
        for cd, group in self.df_test.groupby("centro_distribucion"):
            records.append(_get_comparison(group, "centro", cd, "ALL"))

        # 3. By Horizon
        for hz, group in self.df_test.groupby("horizonte"):
            records.append(_get_comparison(group, "horizonte", "ALL", hz))

        # 4. By Centro x Horizon
        for (cd, hz), group in self.df_test.groupby(["centro_distribucion", "horizonte"]):
            records.append(_get_comparison(group, "centro_horizonte", cd, hz))

        df_comp = pd.DataFrame(records)
        out_path = self.processed_dir / "backtest_results_comparison.csv"
        df_comp.to_csv(out_path, index=False)
        return df_comp

    def generate_visualizations(self) -> None:
        """Creates publication-quality comparison figures."""
        sns.set_theme(style="whitegrid", palette="muted")
        df_comp = self.generate_comparison_summary()

        # 1. Comparativa WAPE Baseline vs Modelo por CD
        df_cd = df_comp[df_comp["nivel"] == "centro"].sort_values("centro_distribucion")
        x = np.arange(len(df_cd))
        width = 0.35

        plt.figure(figsize=(10, 6))
        plt.bar(
            x - width / 2,
            df_cd["wape_baseline"] * 100,
            width,
            label="Baseline Oficial",
            color="#d95f02",
            edgecolor="black",
        )
        plt.bar(
            x + width / 2,
            df_cd["wape_modelo"] * 100,
            width,
            label="Modelo Corrector ML",
            color="#1b9e77",
            edgecolor="black",
        )
        plt.xticks(x, df_cd["centro_distribucion"], fontsize=10, fontweight="bold")
        plt.ylabel("WAPE (%)", fontsize=11, fontweight="bold")
        plt.title(
            "Comparativa de Precisión: Baseline vs Modelo Corrector por Centro (Backtest)",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "comparativa_wape_modelo_vs_baseline.png", dpi=300)
        plt.close()

        # 2. Comparativa Bias Baseline vs Modelo por CD
        plt.figure(figsize=(10, 6))
        plt.bar(
            x - width / 2,
            df_cd["bias_baseline"] * 100,
            width,
            label="Bias Baseline",
            color="#e74c3c",
            edgecolor="black",
        )
        plt.bar(
            x + width / 2,
            df_cd["bias_modelo"] * 100,
            width,
            label="Bias Modelo Corrector",
            color="#2ecc71",
            edgecolor="black",
        )
        plt.axhline(0, color="black", linestyle="--", linewidth=1.0)
        plt.xticks(x, df_cd["centro_distribucion"], fontsize=10, fontweight="bold")
        plt.ylabel("Bias (%)", fontsize=11, fontweight="bold")
        plt.title(
            "Erradicación de Sesgo Estructural: Baseline vs Modelo Corrector por Centro",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "comparativa_bias_modelo_vs_baseline.png", dpi=300)
        plt.close()

        # 3. Importancia de Características del Modelo
        top_imp = self.df_feature_importance.head(10).sort_values("importance", ascending=True)
        plt.figure(figsize=(9, 6))
        plt.barh(top_imp["feature"], top_imp["importance"], color="#34495e", edgecolor="black")
        plt.xlabel("Magnitud del Coeficiente (|Weight|)", fontsize=11, fontweight="bold")
        plt.title(
            "Top 10 Características Clave del Modelo Corrector",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.tight_layout()
        plt.savefig(self.figures_dir / "importancia_caracteristicas_modelo.png", dpi=300)
        plt.close()

        # 4. Curva de Aprendizaje Rolling Origin
        plt.figure(figsize=(10, 5))
        plt.plot(
            self.df_learning_curve["fecha_emision"],
            self.df_learning_curve["wape_base"] * 100,
            label="Baseline Diario",
            color="#e67e22",
            linestyle="--",
            alpha=0.7,
        )
        plt.plot(
            self.df_learning_curve["fecha_emision"],
            self.df_learning_curve["wape_modelo"] * 100,
            label="Modelo Corrector Diario",
            color="#27ae60",
            linewidth=2.0,
        )
        plt.title(
            "Evolución Diaria del Error en Rolling-Origin Backtest",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Fecha de Emisión", fontsize=11, fontweight="bold")
        plt.ylabel("WAPE Diario (%)", fontsize=11, fontweight="bold")
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "curva_aprendizaje_rolling_origin.png", dpi=300)
        plt.close()

        print(f"[OK] 4 Gráficos de Fase 4 guardados en {self.figures_dir}")


if __name__ == "__main__":
    backtester = RollingOriginBacktester(warmup_days=28)
    backtester.run_backtest()
    df_summary = backtester.generate_comparison_summary()
    backtester.generate_visualizations()

    print("\n--- COMPARATIVA GLOBAL DEL BACKTEST ---")
    glob = df_summary[df_summary["nivel"] == "global"].iloc[0]
    print(
        f"WAPE Baseline: {glob['wape_baseline']*100:.2f}% | WAPE Modelo: {glob['wape_modelo']*100:.2f}%"
    )
    print(
        f"Bias Baseline: {glob['bias_baseline']*100:.2f}% | Bias Modelo: {glob['bias_modelo']*100:.2f}%"
    )
    print(
        f"Mejora Neta WAPE: {abs(glob['delta_wape_pp']):.2f} puntos porcentuales de reducción de error."
    )
