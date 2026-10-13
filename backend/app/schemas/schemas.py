"""Pydantic schemas for GlucoTwin Digital Twin API."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Medication(BaseModel):
    name: str
    dose: str
    class_name: str  # e.g., Biguanide, Sulfonylurea, SGLT2i, DPP4i, Insulin


class PatientProfile(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    hba1c: float
    bmi: float
    duration_years: float
    medications: List[Medication]
    baseline_fasting_glucose: float
    baseline_cv: float  # coefficient of variation (%)
    archetype_title: str
    clinical_notes: str
    target_range_min: float = 70.0
    target_range_max: float = 180.0


class CGMReading(BaseModel):
    timestamp: str  # ISO timestamp
    glucose: float  # mg/dL
    carbs: float = 0.0  # grams
    exercise_minutes: float = 0.0
    heart_rate: Optional[float] = None
    step_count: Optional[int] = None


class ForecastPoint(BaseModel):
    horizon_minutes: int
    predicted_glucose: float
    lower_bound: float
    upper_bound: float
    predicted_trend: str  # "rising_fast", "rising", "flat", "falling", "falling_fast"


class AlertInfo(BaseModel):
    is_active: bool
    severity: str  # "normal", "warning", "critical"
    excursion_type: str  # "none", "hypoglycemia", "hyperglycemia"
    lead_time_minutes: Optional[int] = None
    predicted_value: Optional[float] = None
    threshold: Optional[float] = None
    alert_message: str


class FeatureAttribution(BaseModel):
    feature_name: str
    display_name: str
    impact_score: float  # absolute or signed impact
    direction: str  # "elevates", "lowers"
    clinical_explanation: str


class DigitalTwinState(BaseModel):
    patient_id: str
    timestamp: str
    current_glucose: float
    rate_of_change: float  # mg/dL per min
    direction: str  # ↑↑, ↑, →, ↓, ↓↓
    rolling_2h_mean: float
    rolling_2h_std: float
    time_in_range_percent: float
    forecasts: List[ForecastPoint]
    active_alert: AlertInfo
    top_explanations: List[FeatureAttribution]
    total_carbs_last_2h: float
    total_exercise_last_2h: float


class AblationMetric(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_key: str
    display_name: str
    horizon_minutes: int
    mae: float
    rmse: float
    clarke_zone_a: float  # percentage
    clarke_zone_b: float  # percentage
    hypo_sensitivity: float
    hyper_sensitivity: float


class ClarkeGridPoint(BaseModel):
    reference: float
    predicted: float
    zone: str  # "A", "B", "C", "D", "E"


class PatientAblationSummary(BaseModel):
    patient_id: str
    patient_name: str
    hba1c: float
    persistence_mae: float
    fused_mae: float
    mae_improvement_percent: float


class BenchmarkReport(BaseModel):
    horizons: List[int]
    models: List[AblationMetric]
    clarke_sample_points: List[ClarkeGridPoint]
    patient_breakdowns: List[PatientAblationSummary]
    summary_findings: List[str]


class InjectIntervention(BaseModel):
    patient_id: str
    event_type: str  # "meal", "exercise", "medication"
    carbs: float = 0.0
    exercise_minutes: float = 0.0
    description: Optional[str] = None
