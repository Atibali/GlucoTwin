"""Universal dataset loader and cache manager for GlucoTwin India.
Supports native synthetic T2D streams as well as external research CSV formats
(such as OhioT1DM, Dexcom Clarity, and Abbott FreeStyle Libre).
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
from .ehr_generator import get_patient_by_id, get_all_patients
from .t2d_simulator import simulate_patient_cgm

# In-memory cached streams to ensure fast response times across API calls
_STREAM_CACHE: Dict[str, pd.DataFrame] = {}


def get_patient_stream(patient_id: str, num_days: int = 14) -> pd.DataFrame:
    """Retrieve or generate continuous CGM stream for a patient."""
    cache_key = f"{patient_id}_{num_days}d"
    if cache_key in _STREAM_CACHE:
        return _STREAM_CACHE[cache_key].copy()
    
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise ValueError(f"Patient ID '{patient_id}' not found in EHR database.")
    
    df = simulate_patient_cgm(patient=patient, num_days=num_days)
    _STREAM_CACHE[cache_key] = df
    return df.copy()


def load_external_cgm_csv(csv_path: str, patient_id: str = "EXT-001") -> pd.DataFrame:
    """Parse external CGM CSV file into standard GlucoTwin format.
    Standardizes timestamps, glucose (mg/dL), carbs (g), and activity.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    raw = pd.read_csv(csv_path)
    col_map = {c.lower(): c for c in raw.columns}
    
    # Identify timestamp column
    time_col = None
    for candidate in ["timestamp", "time", "date", "datetime", "displaytime"]:
        if candidate in col_map:
            time_col = col_map[candidate]
            break
            
    # Identify glucose column
    glucose_col = None
    for candidate in ["glucose", "glucose_value", "historic glucose mg/dl", "value", "cgm", "bg"]:
        if candidate in col_map:
            glucose_col = col_map[candidate]
            break
            
    if not time_col or not glucose_col:
        raise ValueError("Could not automatically identify timestamp and glucose columns in CSV.")
        
    df = pd.DataFrame()
    df["timestamp"] = pd.to_datetime(raw[time_col]).dt.strftime("%Y-%m-%dT%H:%M:%S")
    df["glucose"] = pd.to_numeric(raw[glucose_col], errors="coerce").fillna(120.0)
    
    # Optional carbs & exercise
    df["carbs"] = 0.0
    for candidate in ["carb", "carbs", "carbohydrates"]:
        if candidate in col_map:
            df["carbs"] = pd.to_numeric(raw[col_map[candidate]], errors="coerce").fillna(0.0)
            break
            
    df["exercise_minutes"] = 0.0
    for candidate in ["exercise", "activity", "steps"]:
        if candidate in col_map:
            df["exercise_minutes"] = pd.to_numeric(raw[col_map[candidate]], errors="coerce").fillna(0.0)
            break
            
    df["heart_rate"] = 75.0
    df["patient_id"] = patient_id
    
    return df
