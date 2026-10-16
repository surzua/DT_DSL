"""Residual demand corrector model."""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.linear_model import Ridge


class ResidualDemandCorrector:
    """
    Complementary analytical model:
    Instead of predicting total demand from scratch, it models the residual error
    of the baseline forecast:
        y_corrected = max(0, y_baseline + epsilon_hat)
    where epsilon_hat = f(X).
    """

    def __init__(self, estimator: Optional[BaseEstimator] = None):
        if estimator is None:
            self.estimator = Ridge(alpha=10.0)
        else:
            self.estimator = estimator
        self.is_fitted = False
        self.feature_names_: List[str] = []

    def fit(self, X: pd.DataFrame, y_residual: pd.Series) -> "ResidualDemandCorrector":
        """Fits the residual estimator on features X and target residual."""
        self.feature_names_ = list(X.columns)
        self.estimator.fit(X, y_residual)
        self.is_fitted = True
        return self

    def predict_residual(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts the residual adjustment."""
        if not self.is_fitted:
            raise ValueError("El modelo corrector no ha sido entrenado todavía.")
        return np.asarray(self.estimator.predict(X[self.feature_names_]))

    def predict_corrected_demand(
        self,
        X: pd.DataFrame,
        base_forecast: pd.Series,
    ) -> np.ndarray:
        """Predicts corrected demand with physical non-negativity constraint."""
        pred_res = self.predict_residual(X)
        corrected = np.maximum(0.0, np.asarray(base_forecast) + pred_res)
        return corrected

    def get_feature_importance(self) -> pd.DataFrame:
        """Returns sorted feature importances or model coefficients."""
        if not self.is_fitted:
            raise ValueError("El modelo corrector no ha sido entrenado todavía.")

        if hasattr(self.estimator, "coef_"):
            weights = np.abs(self.estimator.coef_)
            raw_weights = self.estimator.coef_
        elif hasattr(self.estimator, "feature_importances_"):
            weights = self.estimator.feature_importances_
            raw_weights = self.estimator.feature_importances_
        else:
            weights = np.ones(len(self.feature_names_))
            raw_weights = weights

        df_imp = pd.DataFrame(
            {
                "feature": self.feature_names_,
                "importance": weights,
                "raw_coefficient": raw_weights,
            }
        ).sort_values("importance", ascending=False).reset_index(drop=True)
        return df_imp
