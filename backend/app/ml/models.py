"""Forecasting models for GlucoTwin India.
Implements Persistence baseline, Ridge linear baseline, and XGBoost / Gradient Boosting
multi-horizon regressors with uncertainty estimation and personalized calibration.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor
from .features import SENSOR_FEATURE_COLS, EHR_FEATURE_COLS, FUSED_FEATURE_COLS


class PersistenceModel:
    """Standard clinical baseline: predicts current reading for future horizon."""
    def __init__(self, with_drift: bool = False):
        self.with_drift = with_drift
        
    def predict(self, X: pd.DataFrame, horizon_minutes: int = 30) -> np.ndarray:
        current = X["glucose_current"].values
        if not self.with_drift or "velocity_5m" not in X:
            return current
        # Damped drift: velocity * horizon * damping factor
        drift = X["velocity_5m"].values * (horizon_minutes * 0.4)
        return current + drift


class GlucoTwinForecaster:
    """Multi-horizon Gradient Boosted Tree forecaster with uncertainty estimation."""
    def __init__(self, feature_mode: str = "fused"):
        """
        feature_mode:
          - "sensor": only dynamic CGM rolling features
          - "ehr": only static EHR features
          - "fused": combined sensor + EHR features
        """
        self.feature_mode = feature_mode
        if feature_mode == "sensor":
            self.feature_cols = SENSOR_FEATURE_COLS
        elif feature_mode == "ehr":
            self.feature_cols = EHR_FEATURE_COLS
        else:
            self.feature_cols = FUSED_FEATURE_COLS
            
        self.models: Dict[int, XGBRegressor] = {}
        self.residual_stds: Dict[int, float] = {}

    def fit(self, X: pd.DataFrame, y_dict: Dict[int, np.ndarray]):
        """Fit separate XGBoost regressors for each forecast horizon."""
        X_sub = X[self.feature_cols].copy()
        
        for horizon, y in y_dict.items():
            model = XGBRegressor(
                n_estimators=120,
                max_depth=4,
                learning_rate=0.06,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=42,
                n_jobs=2
            )
            model.fit(X_sub, y)
            self.models[horizon] = model
            
            # Compute empirical residual standard deviation for uncertainty intervals
            preds = model.predict(X_sub)
            self.residual_stds[horizon] = float(np.std(y - preds))

    def predict(
        self,
        X: pd.DataFrame,
        horizon_minutes: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns point prediction, lower 80% bound (10th percentile), upper 80% bound (90th percentile)."""
        if horizon_minutes not in self.models:
            raise ValueError(f"No model trained for horizon {horizon_minutes}m")
            
        X_sub = X[self.feature_cols].copy()
        point_pred = self.models[horizon_minutes].predict(X_sub)
        
        # 80% prediction interval z = 1.282
        sigma = self.residual_stds.get(horizon_minutes, 10.0)
        z = 1.282
        lower = point_pred - z * sigma
        upper = point_pred + z * sigma
        
        # Clip to physiological bounds
        lower = np.clip(lower, 40.0, 400.0)
        upper = np.clip(upper, 40.0, 400.0)
        
        return point_pred, lower, upper

    def get_feature_importances(self, horizon_minutes: int = 30) -> Dict[str, float]:
        """Extract Gini feature importances for a given horizon."""
        if horizon_minutes not in self.models:
            return {}
        model = self.models[horizon_minutes]
        importances = model.feature_importances_
        return {col: float(imp) for col, imp in zip(self.feature_cols, importances)}
