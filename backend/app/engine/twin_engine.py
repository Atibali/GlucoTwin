"""Digital Twin State Engine for GlucoTwin India.
Maintains continuous rolling state buffers, fuses longitudinal clinical records,
generates multi-horizon forecasts with uncertainty intervals, and triggers
early-warning excursion risk flags.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from ..schemas.schemas import (
    PatientProfile, CGMReading, ForecastPoint, AlertInfo,
    DigitalTwinState, FeatureAttribution
)
from ..ml.features import (
    compute_rolling_features_from_buffer, extract_ehr_features,
    FUSED_FEATURE_COLS
)
from ..ml.models import GlucoTwinForecaster
from ..ml.explainer import explain_prediction
from ..core.config import settings


class PatientDigitalTwin:
    """Virtual patient replica maintaining real-time glycemic state."""
    
    def __init__(self, patient: PatientProfile, forecaster: Optional[GlucoTwinForecaster] = None):
        self.patient = patient
        self.forecaster = forecaster
        
        # Static EHR feature vector
        self.ehr_features = extract_ehr_features(patient)
        
        # Dynamic state buffers (at least 28 steps = 140 mins)
        self.buffer_size = 36
        self.glucose_buffer: List[float] = []
        self.carbs_buffer: List[float] = []
        self.exercise_buffer: List[float] = []
        self.timestamp_buffer: List[pd.Timestamp] = []
        
        # Running 24-hour reading history for TIR calculation
        self.history_24h: List[float] = []

    def initialize_with_history(self, seed_readings: List[CGMReading]):
        """Warm up the twin buffer with initial historical readings."""
        self.glucose_buffer.clear()
        self.carbs_buffer.clear()
        self.exercise_buffer.clear()
        self.timestamp_buffer.clear()
        self.history_24h.clear()
        
        for r in seed_readings:
            self.ingest_reading(r)

    def ingest_reading(self, reading: CGMReading):
        """Append a new 5-minute CGM reading into the twin's rolling state."""
        dt = pd.to_datetime(reading.timestamp)
        self.glucose_buffer.append(float(reading.glucose))
        self.carbs_buffer.append(float(reading.carbs))
        self.exercise_buffer.append(float(reading.exercise_minutes))
        self.timestamp_buffer.append(dt)
        
        self.history_24h.append(float(reading.glucose))
        if len(self.history_24h) > 288:  # 24 hours * 12 readings/hr
            self.history_24h.pop(0)
            
        # Maintain buffer length
        if len(self.glucose_buffer) > self.buffer_size:
            self.glucose_buffer.pop(0)
            self.carbs_buffer.pop(0)
            self.exercise_buffer.pop(0)
            self.timestamp_buffer.pop(0)

    def _determine_direction(self, v_5m: float) -> Tuple[str, str]:
        """Convert rate of change into clinical trend arrow and text."""
        if v_5m > 2.0:
            return "↑↑", "rising_fast"
        elif v_5m > 0.8:
            return "↑", "rising"
        elif v_5m < -2.0:
            return "↓↓", "falling_fast"
        elif v_5m < -0.8:
            return "↓", "falling"
        else:
            return "→", "flat"

    def compute_state(self) -> DigitalTwinState:
        """Evaluate the current twin state, forecasts, uncertainty bounds, and alerts."""
        if len(self.glucose_buffer) < 4:
            raise ValueError("Insufficient readings to compute digital twin state (need at least 4).")
            
        g_arr = np.array(self.glucose_buffer)
        c_arr = np.array(self.carbs_buffer)
        e_arr = np.array(self.exercise_buffer)
        current_time = self.timestamp_buffer[-1]
        
        current_glucose = float(g_arr[-1])
        
        # Extract features
        rolling_feats = compute_rolling_features_from_buffer(g_arr, c_arr, e_arr, current_time)
        fused_dict = {**rolling_feats, **self.ehr_features}
        X_current = pd.DataFrame([fused_dict])
        
        v_5m = rolling_feats["velocity_5m"]
        arrow, trend_text = self._determine_direction(v_5m)
        
        # Forecasts
        forecast_points: List[ForecastPoint] = []
        lead_time_hypo = None
        lead_time_hyper = None
        critical_forecast_val = None
        
        horizons = [30, 60, 120]
        for h in horizons:
            if self.forecaster and h in self.forecaster.models:
                point_pred, lower, upper = self.forecaster.predict(X_current, horizon_minutes=h)
                pred_val = float(point_pred[0])
                lower_val = float(lower[0])
                upper_val = float(upper[0])
            else:
                # Damped drift fallback if no trained model loaded
                pred_val = current_glucose + v_5m * (h * 0.5)
                pred_val = float(np.clip(pred_val, 40.0, 380.0))
                lower_val = max(40.0, pred_val - (8.0 + h * 0.15))
                upper_val = min(400.0, pred_val + (8.0 + h * 0.15))
                
            pred_v = (pred_val - current_glucose) / float(h)
            _, p_trend = self._determine_direction(pred_v)
            
            forecast_points.append(ForecastPoint(
                horizon_minutes=h,
                predicted_glucose=round(pred_val, 1),
                lower_bound=round(lower_val, 1),
                upper_bound=round(upper_val, 1),
                predicted_trend=p_trend
            ))
            
            # Check for threshold crossings
            if pred_val < settings.HYPOGLYCEMIA_THRESHOLD and lead_time_hypo is None:
                lead_time_hypo = h
                critical_forecast_val = pred_val
            elif pred_val > settings.HYPERGLYCEMIA_THRESHOLD and lead_time_hyper is None:
                lead_time_hyper = h
                critical_forecast_val = pred_val
                
        # Evaluate Early Warning Alert
        if lead_time_hypo is not None:
            severity = "critical" if critical_forecast_val < settings.SEVERE_HYPO_THRESHOLD else "warning"
            alert = AlertInfo(
                is_active=True,
                severity=severity,
                excursion_type="hypoglycemia",
                lead_time_minutes=lead_time_hypo,
                predicted_value=round(critical_forecast_val, 1),
                threshold=settings.HYPOGLYCEMIA_THRESHOLD,
                alert_message=f"Impending Hypoglycemia alert: Glucose forecast to reach {critical_forecast_val:.0f} mg/dL within ~{lead_time_hypo} minutes. Consider preventive fast-acting carbs."
            )
        elif lead_time_hyper is not None:
            severity = "critical" if critical_forecast_val > settings.SEVERE_HYPER_THRESHOLD else "warning"
            alert = AlertInfo(
                is_active=True,
                severity=severity,
                excursion_type="hyperglycemia",
                lead_time_minutes=lead_time_hyper,
                predicted_value=round(critical_forecast_val, 1),
                threshold=settings.HYPERGLYCEMIA_THRESHOLD,
                alert_message=f"Impending Hyperglycemia excursion: Predicted to exceed {settings.HYPERGLYCEMIA_THRESHOLD:.0f} mg/dL ({critical_forecast_val:.0f} mg/dL) in ~{lead_time_hyper} minutes."
            )
        else:
            alert = AlertInfo(
                is_active=False,
                severity="normal",
                excursion_type="none",
                alert_message="Glycemic levels stable within target clinical bounds (70 - 180 mg/dL)."
            )
            
        # Explanations for 30m forecast
        pred_30m = forecast_points[0].predicted_glucose
        explanations = explain_prediction(fused_dict, self.patient, pred_30m, current_glucose)
        
        # Time in range % (70 - 180 mg/dL)
        hist_arr = np.array(self.history_24h)
        tir = float(np.mean((hist_arr >= 70.0) & (hist_arr <= 180.0)) * 100.0) if len(hist_arr) > 0 else 85.0
        
        # 2h stats
        g_2h = g_arr[-24:] if len(g_arr) >= 24 else g_arr
        mean_2h = float(np.mean(g_2h))
        std_2h = float(np.std(g_2h))
        
        carbs_2h = float(np.sum(c_arr[-24:]))
        ex_2h = float(np.sum(e_arr[-24:]))
        
        return DigitalTwinState(
            patient_id=self.patient.patient_id,
            timestamp=current_time.isoformat(),
            current_glucose=round(current_glucose, 1),
            rate_of_change=round(v_5m, 2),
            direction=arrow,
            rolling_2h_mean=round(mean_2h, 1),
            rolling_2h_std=round(std_2h, 1),
            time_in_range_percent=round(tir, 1),
            forecasts=forecast_points,
            active_alert=alert,
            top_explanations=explanations,
            total_carbs_last_2h=round(carbs_2h, 1),
            total_exercise_last_2h=round(ex_2h, 1),
        )
