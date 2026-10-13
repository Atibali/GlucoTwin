"""Feature engineering and multimodal data fusion pipeline for GlucoTwin.
Extracts dynamic rolling temporal features from CGM streams and fuses them
with static longitudinal EHR patient profile vectors.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from ..schemas.schemas import PatientProfile


SENSOR_FEATURE_COLS = [
    "glucose_current",
    "velocity_5m",
    "velocity_15m",
    "velocity_30m",
    "acceleration_5m",
    "rolling_mean_30m",
    "rolling_mean_60m",
    "rolling_mean_120m",
    "rolling_std_60m",
    "rolling_std_120m",
    "rolling_min_120m",
    "rolling_max_120m",
    "carb_decay_2h",
    "exercise_decay_2h",
    "sin_time_of_day",
    "cos_time_of_day",
]

EHR_FEATURE_COLS = [
    "age",
    "bmi",
    "hba1c",
    "duration_years",
    "baseline_fasting_glucose",
    "baseline_cv",
    "med_metformin",
    "med_sulfonylurea",
    "med_sglt2",
    "med_insulin",
    "med_dpp4",
]

FUSED_FEATURE_COLS = SENSOR_FEATURE_COLS + EHR_FEATURE_COLS


def extract_ehr_features(patient: PatientProfile) -> Dict[str, float]:
    """Encode static clinical EHR profile into numerical feature vector."""
    med_classes = " ".join([m.class_name for m in patient.medications])
    
    return {
        "age": float(patient.age),
        "bmi": float(patient.bmi),
        "hba1c": float(patient.hba1c),
        "duration_years": float(patient.duration_years),
        "baseline_fasting_glucose": float(patient.baseline_fasting_glucose),
        "baseline_cv": float(patient.baseline_cv),
        "med_metformin": 1.0 if "Biguanide" in med_classes or "Metformin" in med_classes else 0.0,
        "med_sulfonylurea": 1.0 if "Sulfonylurea" in med_classes else 0.0,
        "med_sglt2": 1.0 if "SGLT2" in med_classes else 0.0,
        "med_insulin": 1.0 if "Insulin" in med_classes else 0.0,
        "med_dpp4": 1.0 if "DPP-4" in med_classes else 0.0,
    }


def compute_rolling_features_from_buffer(
    glucose_buffer: np.ndarray,
    carbs_buffer: np.ndarray,
    exercise_buffer: np.ndarray,
    current_time_dt: pd.Timestamp
) -> Dict[str, float]:
    """Compute rolling features for an in-memory buffer of the last 24 steps (2 hours)."""
    # Ensure buffer has at least 24 steps
    n = len(glucose_buffer)
    g_curr = float(glucose_buffer[-1])
    
    # Velocities (mg/dL per minute)
    v_5m = (g_curr - float(glucose_buffer[-2])) / 5.0 if n >= 2 else 0.0
    v_15m = (g_curr - float(glucose_buffer[-4])) / 15.0 if n >= 4 else v_5m
    v_30m = (g_curr - float(glucose_buffer[-7])) / 30.0 if n >= 7 else v_15m
    
    v_prev_5m = (float(glucose_buffer[-2]) - float(glucose_buffer[-3])) / 5.0 if n >= 3 else v_5m
    accel_5m = (v_5m - v_prev_5m) / 5.0
    
    # Rolling stats
    # 30m = 6 steps, 60m = 12 steps, 120m = 24 steps
    g_30m = glucose_buffer[-6:] if n >= 6 else glucose_buffer
    g_60m = glucose_buffer[-12:] if n >= 12 else glucose_buffer
    g_120m = glucose_buffer[-24:] if n >= 24 else glucose_buffer
    
    mean_30m = float(np.mean(g_30m))
    mean_60m = float(np.mean(g_60m))
    mean_120m = float(np.mean(g_120m))
    std_60m = float(np.std(g_60m))
    std_120m = float(np.std(g_120m))
    min_120m = float(np.min(g_120m))
    max_120m = float(np.max(g_120m))
    
    # Exponential decay weights for carbs and exercise
    # Steps: 0 is current (delta_t = 0), -1 is 5m ago, etc.
    step_indices = np.arange(len(carbs_buffer))[::-1]  # 0, 1, 2, ...
    delta_minutes = step_indices * 5.0
    
    carb_decay_weights = np.exp(-0.025 * delta_minutes)
    exercise_decay_weights = np.exp(-0.035 * delta_minutes)
    
    carb_decay = float(np.sum(carbs_buffer * carb_decay_weights))
    exercise_decay = float(np.sum(exercise_buffer * exercise_decay_weights))
    
    # Circadian sin/cos
    hour_float = current_time_dt.hour + current_time_dt.minute / 60.0
    sin_tod = float(np.sin(2 * np.pi * hour_float / 24.0))
    cos_tod = float(np.cos(2 * np.pi * hour_float / 24.0))
    
    return {
        "glucose_current": g_curr,
        "velocity_5m": v_5m,
        "velocity_15m": v_15m,
        "velocity_30m": v_30m,
        "acceleration_5m": accel_5m,
        "rolling_mean_30m": mean_30m,
        "rolling_mean_60m": mean_60m,
        "rolling_mean_120m": mean_120m,
        "rolling_std_60m": std_60m,
        "rolling_std_120m": std_120m,
        "rolling_min_120m": min_120m,
        "rolling_max_120m": max_120m,
        "carb_decay_2h": carb_decay,
        "exercise_decay_2h": exercise_decay,
        "sin_time_of_day": sin_tod,
        "cos_time_of_day": cos_tod,
    }


def build_feature_dataset(
    df: pd.DataFrame,
    patient: PatientProfile,
    horizons_steps: Dict[int, int] = {30: 6, 60: 12, 120: 24}
) -> Tuple[pd.DataFrame, Dict[int, np.ndarray]]:
    """Transform sequential CGM dataframe into supervised tabular feature dataset."""
    df_sorted = df.copy()
    df_sorted["dt"] = pd.to_datetime(df_sorted["timestamp"])
    df_sorted = df_sorted.sort_values("dt").reset_index(drop=True)
    
    glucose_vals = df_sorted["glucose"].values
    carbs_vals = df_sorted["carbs"].values
    exercise_vals = df_sorted["exercise_minutes"].values
    timestamps = df_sorted["dt"].values
    
    ehr_feats = extract_ehr_features(patient)
    
    # We require at least 24 steps of history buffer (2 hours)
    start_idx = 24
    max_horizon_step = max(horizons_steps.values())
    end_idx = len(df_sorted) - max_horizon_step
    
    records = []
    targets: Dict[int, List[float]] = {h: [] for h in horizons_steps}
    
    for i in range(start_idx, end_idx):
        g_slice = glucose_vals[i-24:i+1]
        c_slice = carbs_vals[i-24:i+1]
        e_slice = exercise_vals[i-24:i+1]
        cur_ts = pd.Timestamp(timestamps[i])
        
        sensor_feats = compute_rolling_features_from_buffer(g_slice, c_slice, e_slice, cur_ts)
        # Fuse sensor + EHR
        combined = {**sensor_feats, **ehr_feats}
        records.append(combined)
        
        for h_min, h_step in horizons_steps.items():
            targets[h_min].append(glucose_vals[i + h_step])
            
    X_df = pd.DataFrame(records)
    y_arrays = {h: np.array(targets[h]) for h in horizons_steps}
    return X_df, y_arrays
