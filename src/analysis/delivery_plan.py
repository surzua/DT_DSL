"""Operational delivery plan analysis, capacity saturation, and demand smoothing (Tarea 2)."""

from pathlib import Path
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.data.loader import (
    load_processed_plan_entrega,
    load_processed_demanda,
    load_processed_capacidad,
)

DEFAULT_FIGURES_DIR = Path("reports/figures/fase_03")
DEFAULT_PROCESSED_DIR = Path("data/processed")


class DeliveryPlanAnalyzer:
    """Analyzes customer plan adherence, capacity bottlenecks, and demand smoothing opportunities."""

    def __init__(
        self,
        df_plan: pd.DataFrame = None,
        df_demanda: pd.DataFrame = None,
        df_capacidad: pd.DataFrame = None,
        figures_dir: Path = DEFAULT_FIGURES_DIR,
        processed_dir: Path = DEFAULT_PROCESSED_DIR,
    ):
        self.df_plan = df_plan if df_plan is not None else load_processed_plan_entrega()
        self.df_demanda = df_demanda if df_demanda is not None else load_processed_demanda()
        self.df_capacidad = df_capacidad if df_capacidad is not None else load_processed_capacidad()
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = Path(processed_dir)

        # Feature enrichment for plan
        self.df_plan["delta_dias"] = (
            self.df_plan["fecha_compra_real"] - self.df_plan["fecha_plan"]
        ).dt.days
        self.df_plan["dia_semana_plan"] = self.df_plan["fecha_plan"].dt.day_name()
        self.df_plan["dia_semana_real"] = self.df_plan["fecha_compra_real"].dt.day_name()
        self.df_plan["dia_num_plan"] = self.df_plan["fecha_plan"].dt.dayofweek

    def calculate_plan_bias(self) -> Dict[str, float]:
        """Calculates volume and date bias between commercial plan and actual purchases."""
        total_plan = float(self.df_plan["unidades_plan"].sum())
        total_real = float(self.df_plan["unidades_reales"].sum())
        bias_unidades = (total_real - total_plan) / total_real if total_real != 0 else 0.0

        mean_delta_dias = float(self.df_plan["delta_dias"].mean())
        median_delta_dias = float(self.df_plan["delta_dias"].median())

        # Directional breakdown of out-of-plan purchases
        fuera = self.df_plan[self.df_plan["fuera_de_plan"] == 1]
        adelantadas = int((fuera["delta_dias"] < 0).sum())
        retrasadas = int((fuera["delta_dias"] > 0).sum())

        return {
            "total_unidades_plan": total_plan,
            "total_unidades_reales": total_real,
            "bias_unidades_pct": bias_unidades * 100.0,
            "mean_delta_dias": mean_delta_dias,
            "median_delta_dias": median_delta_dias,
            "total_pedidos": len(self.df_plan),
            "total_fuera_de_plan": int(self.df_plan["fuera_de_plan"].sum()),
            "pct_fuera_de_plan": float(self.df_plan["fuera_de_plan"].mean() * 100.0),
            "compras_adelantadas": adelantadas,
            "compras_retrasadas": retrasadas,
            "late_to_early_ratio": retrasadas / adelantadas if adelantadas > 0 else 0.0,
        }

    def analyze_fuera_de_plan_by_cd(self) -> pd.DataFrame:
        """Analyzes out-of-plan rate broken down by distribution center."""
        df_cd = (
            self.df_plan.groupby("centro_distribucion")
            .agg(
                total_pedidos=("fuera_de_plan", "count"),
                pedidos_fuera=("fuera_de_plan", "sum"),
                pct_fuera_de_plan=("fuera_de_plan", lambda x: x.mean() * 100.0),
                unidades_plan_sum=("unidades_plan", "sum"),
                unidades_reales_sum=("unidades_reales", "sum"),
                delta_dias_promedio=("delta_dias", "mean"),
            )
            .reset_index()
        )
        df_cd["bias_unidades_pct"] = (
            (df_cd["unidades_reales_sum"] - df_cd["unidades_plan_sum"])
            / df_cd["unidades_reales_sum"]
        ) * 100.0
        return df_cd.sort_values("pct_fuera_de_plan", ascending=False).reset_index(drop=True)

    def analyze_fuera_de_plan_by_day(self) -> pd.DataFrame:
        """Analyzes out-of-plan rate by planned day of the week."""
        day_mapping = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes",
            "Saturday": "Sábado",
            "Sunday": "Domingo",
        }
        df_day = (
            self.df_plan.groupby(["dia_num_plan", "dia_semana_plan"])
            .agg(
                total_pedidos=("fuera_de_plan", "count"),
                pedidos_fuera=("fuera_de_plan", "sum"),
                pct_fuera_de_plan=("fuera_de_plan", lambda x: x.mean() * 100.0),
                unidades_plan_sum=("unidades_plan", "sum"),
                unidades_reales_sum=("unidades_reales", "sum"),
            )
            .reset_index()
            .sort_values("dia_num_plan")
        )
        df_day["dia_semana_es"] = df_day["dia_semana_plan"].map(day_mapping)
        return df_day

    def calculate_customer_adherence(self) -> pd.DataFrame:
        """
        Computes granular plan adherence per customer (identifies high-volatility accounts / Pareto).
        Saves to data/processed/analisis_adhesion_clientes.csv.
        """
        df_cust = (
            self.df_plan.groupby(["cliente_id", "centro_distribucion"])
            .agg(
                total_pedidos=("fuera_de_plan", "count"),
                pedidos_en_plan=("fuera_de_plan", lambda x: (x == 0).sum()),
                pedidos_fuera_plan=("fuera_de_plan", "sum"),
                tasa_adhesion_pct=("fuera_de_plan", lambda x: (1.0 - x.mean()) * 100.0),
                unidades_plan_total=("unidades_plan", "sum"),
                unidades_reales_total=("unidades_reales", "sum"),
                delta_dias_promedio=("delta_dias", "mean"),
            )
            .reset_index()
        )
        df_cust["bias_volumen_pct"] = (
            (df_cust["unidades_reales_total"] - df_cust["unidades_plan_total"])
            / df_cust["unidades_reales_total"]
        ) * 100.0

        out_path = self.processed_dir / "analisis_adhesion_clientes.csv"
        df_cust.to_csv(out_path, index=False)
        return df_cust

    def analyze_capacity_saturation(self) -> pd.DataFrame:
        """
        Crosses daily aggregated demand with maximum logistic capacity per CD.
        Identifies bottleneck days, saturation rates, and emergency freight exposure.
        Saves to data/processed/saturacion_capacidad_cd.csv.
        """
        merged = pd.merge(
            self.df_demanda,
            self.df_capacidad,
            left_on=["centro_distribucion", "fecha_despacho"],
            right_on=["centro_distribucion", "fecha"],
            how="inner",
        )
        merged["ocupacion_pct"] = (
            merged["unidades_reales_total"] / merged["capacidad_maxima_unidades"]
        ) * 100.0
        merged["saturado"] = (merged["ocupacion_pct"] > 100.0).astype(int)
        merged["exceso_unidades"] = np.maximum(
            0.0, merged["unidades_reales_total"] - merged["capacidad_maxima_unidades"]
        )

        df_sat = (
            merged.groupby("centro_distribucion")
            .agg(
                dias_totales=("fecha", "count"),
                dias_saturados=("saturado", "sum"),
                pct_dias_saturados=("saturado", lambda x: x.mean() * 100.0),
                ocupacion_promedio_pct=("ocupacion_pct", "mean"),
                ocupacion_maxima_pct=("ocupacion_pct", "max"),
                exceso_unidades_total=("exceso_unidades", "sum"),
            )
            .reset_index()
        )

        out_path = self.processed_dir / "saturacion_capacidad_cd.csv"
        df_sat.to_csv(out_path, index=False)
        return df_sat

    def generate_visualizations(self) -> None:
        """Generates visual figures for Tarea 2."""
        sns.set_theme(style="whitegrid", palette="muted")

        # 1. Fuera de plan por día de la semana planificado
        df_day = self.analyze_fuera_de_plan_by_day()
        plt.figure(figsize=(9, 5))
        bars = plt.bar(
            df_day["dia_semana_es"],
            df_day["pct_fuera_de_plan"],
            color="#2b5c8f",
            edgecolor="black",
            alpha=0.85,
        )
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                yval + 0.6,
                f"{yval:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )
        plt.title(
            "Tasa de Compras Fuera de Plan (%) por Día de la Semana Planificado",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Día de la Semana Planificado", fontsize=11, fontweight="bold")
        plt.ylabel("% Compras Fuera de Plan", fontsize=11, fontweight="bold")
        plt.ylim(0, 30)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "compras_fuera_plan_por_dia_semana.png", dpi=300)
        plt.close()

        # 2. Tasa de Fuera de Plan por Centro de Distribución
        df_cd = self.analyze_fuera_de_plan_by_cd()
        plt.figure(figsize=(9, 5))
        bars = plt.bar(
            df_cd["centro_distribucion"],
            df_cd["pct_fuera_de_plan"],
            color=["#c0392b" if p > 20 else "#2980b9" for p in df_cd["pct_fuera_de_plan"]],
            edgecolor="black",
            alpha=0.85,
        )
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                yval + 0.6,
                f"{yval:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )
        plt.axhline(17.46, color="black", linestyle="--", linewidth=1.2, label="Promedio Red (17.5%)")
        plt.title(
            "Tasa de Desvío Fuera de Plan por Centro de Distribución",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Centro de Distribución", fontsize=11, fontweight="bold")
        plt.ylabel("% Compras Fuera de Plan", fontsize=11, fontweight="bold")
        plt.ylim(0, 32)
        plt.legend(loc="upper right")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "fuera_plan_por_cd.png", dpi=300)
        plt.close()

        # 3. Distribución del Desvío Temporal (Delta días)
        plt.figure(figsize=(9, 5))
        delta_counts = self.df_plan["delta_dias"].value_counts().sort_index()
        bars = plt.bar(
            delta_counts.index,
            delta_counts.values,
            color=["#27ae60" if d == 0 else "#e67e22" if d > 0 else "#8e44ad" for d in delta_counts.index],
            edgecolor="black",
        )
        plt.title(
            "Distribución del Desvío Temporal (Días Real - Días Plan)",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel(
            "Diferencia en Días (Negativo: Adelantado | 0: Exacto | Positivo: Retrasado)",
            fontsize=11,
            fontweight="bold",
        )
        plt.ylabel("Número de Pedidos", fontsize=11, fontweight="bold")
        plt.tight_layout()
        plt.savefig(self.figures_dir / "distribucion_delta_dias.png", dpi=300)
        plt.close()

        # 4. Saturación de Capacidad por CD
        df_sat = self.analyze_capacity_saturation()
        plt.figure(figsize=(9, 5))
        bars = plt.bar(
            df_sat["centro_distribucion"],
            df_sat["pct_dias_saturados"],
            color=["#c0392b" if s >= 10 else "#d35400" if s > 0 else "#27ae60" for s in df_sat["pct_dias_saturados"]],
            edgecolor="black",
        )
        for bar in bars:
            yval = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                yval + 0.3,
                f"{yval:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )
        plt.title(
            "Porcentaje de Días con Saturación de Capacidad (>100%) por CD",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )
        plt.xlabel("Centro de Distribución", fontsize=11, fontweight="bold")
        plt.ylabel("% de Días con Exceso de Capacidad", fontsize=11, fontweight="bold")
        plt.ylim(0, 14)
        plt.tight_layout()
        plt.savefig(self.figures_dir / "saturacion_capacidad_cd.png", dpi=300)
        plt.close()

        print(f"[OK] 4 Gráficos de Fase 3 guardados en {self.figures_dir}")

    def run_full_analysis(self) -> Dict:
        """Executes full analysis suite for Tarea 2."""
        bias_info = self.calculate_plan_bias()
        df_cd = self.analyze_fuera_de_plan_by_cd()
        df_day = self.analyze_fuera_de_plan_by_day()
        df_cust = self.calculate_customer_adherence()
        df_sat = self.analyze_capacity_saturation()
        self.generate_visualizations()

        return {
            "bias_info": bias_info,
            "by_cd": df_cd,
            "by_day": df_day,
            "customers": df_cust,
            "capacity": df_sat,
        }


if __name__ == "__main__":
    analyzer = DeliveryPlanAnalyzer()
    res = analyzer.run_full_analysis()
    print("\n--- RESUMEN DE PLAN DE ENTREGA ---")
    for k, v in res["bias_info"].items():
        print(f"  {k}: {v}")
