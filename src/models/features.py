"""Feature engineering pipeline for demand forecasting and residual correction."""

from typing import List, Tuple
import numpy as np
import pandas as pd


class DemandFeaturePipeline:
    """
    Extracts calendar, baseline, and historical rolling features.
    Enforces strict temporal separation: rolling metrics only use data available
    prior to fecha_emision (zero data leakage).
    """

    def __init__(self, rolling_windows: Tuple[int, ...] = (7, 14, 21)):
        self.rolling_windows = rolling_windows
        self.feature_columns: List[str] = []

    def fit_transform(
        self,
        df_pronostico: pd.DataFrame,
        df_demanda_real: pd.DataFrame,
    ) -> pd.DataFrame:
        """Constructs features for the entire forecast dataset."""
        df_pron = df_pronostico.copy()
        df_dem = df_demanda_real.sort_values(
            ["centro_distribucion", "fecha_despacho"]
        ).reset_index(drop=True)

        features = []
        for _, row in df_pron.iterrows():
            cd = row["centro_distribucion"]
            emision = pd.to_datetime(row["fecha_emision"])
            despacho = pd.to_datetime(row["fecha_despacho"])
            horiz_str = str(row["horizonte"])
            horiz_num = int(horiz_str.replace("D+", ""))
            base_pred = float(row["unidades_pronosticadas"])
            real = float(row["unidades_reales"])

            # Strict temporal constraint: only use demand strictly prior to emision date
            hist = df_dem[
                (df_dem["centro_distribucion"] == cd)
                & (pd.to_datetime(df_dem["fecha_despacho"]) < emision)
            ]

            # Rolling statistics
            feat_dict = {
                "centro_distribucion": cd,
                "fecha_emision": emision,
                "fecha_despacho": despacho,
                "horizonte": horiz_str,
                "horizonte_num": horiz_num,
                "unidades_pronosticadas": base_pred,
                "unidades_reales": real,
                "residual": real - base_pred,
                # Calendar features
                "dia_semana_despacho": despacho.dayofweek,
                "es_martes": 1.0 if despacho.dayofweek == 1 else 0.0,
                "es_lunes": 1.0 if despacho.dayofweek == 0 else 0.0,
                "es_fin_de_semana": 1.0 if despacho.dayofweek in [5, 6] else 0.0,
                "dia_mes": float(despacho.day),
            }

            for w in self.rolling_windows:
                if len(hist) >= w:
                    w_vals = hist.tail(w)["unidades_reales_total"]
                    feat_dict[f"mean_{w}d"] = float(w_vals.mean())
                    feat_dict[f"std_{w}d"] = float(w_vals.std()) if len(w_vals) > 1 else 0.0
                elif len(hist) > 0:
                    feat_dict[f"mean_{w}d"] = float(hist["unidades_reales_total"].mean())
                    feat_dict[f"std_{w}d"] = (
                        float(hist["unidades_reales_total"].std()) if len(hist) > 1 else 0.0
                    )
                else:
                    feat_dict[f"mean_{w}d"] = base_pred
                    feat_dict[f"std_{w}d"] = 0.0

            # Signal interactions
            feat_dict["ratio_base_to_mean7"] = (
                base_pred / (feat_dict["mean_7d"] + 1e-4)
                if feat_dict["mean_7d"] > 0
                else 1.0
            )

            features.append(feat_dict)

        df_feat = pd.DataFrame(features)

        # Retain original centro_distribucion for grouping and slicing
        orig_centros = df_feat["centro_distribucion"].copy()

        # One-hot encoding of distribution centers
        dummies = pd.get_dummies(
            df_feat["centro_distribucion"], prefix="centro_distribucion", dtype=float
        )
        df_feat = pd.concat([df_feat, dummies], axis=1)

        # Explicit center interaction with Tuesday peak
        for cd_col in dummies.columns:
            df_feat[f"{cd_col}_x_martes"] = df_feat[cd_col] * df_feat["es_martes"]

        # Track model feature columns (exclude dates, targets, and original string ID)
        exclude_cols = {
            "centro_distribucion",
            "fecha_emision",
            "fecha_despacho",
            "horizonte",
            "unidades_reales",
            "residual",
        }
        self.feature_columns = [c for c in df_feat.columns if c not in exclude_cols]

        return df_feat
