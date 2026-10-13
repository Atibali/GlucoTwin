export interface Medication {
  name: string;
  dose: string;
  class_name: string;
}

export interface PatientProfile {
  patient_id: string;
  name: string;
  age: number;
  gender: string;
  hba1c: number;
  bmi: number;
  duration_years: number;
  medications: Medication[];
  baseline_fasting_glucose: number;
  baseline_cv: number;
  archetype_title: string;
  clinical_notes: string;
  target_range_min: number;
  target_range_max: number;
}

export interface ForecastPoint {
  horizon_minutes: number;
  predicted_glucose: number;
  lower_bound: number;
  upper_bound: number;
  predicted_trend: string;
}

export interface AlertInfo {
  is_active: boolean;
  severity: "normal" | "warning" | "critical";
  excursion_type: "none" | "hypoglycemia" | "hyperglycemia";
  lead_time_minutes?: number;
  predicted_value?: number;
  threshold?: number;
  alert_message: string;
}

export interface FeatureAttribution {
  feature_name: string;
  display_name: string;
  impact_score: number;
  direction: "elevates" | "lowers";
  clinical_explanation: string;
}

export interface DigitalTwinState {
  patient_id: string;
  timestamp: string;
  current_glucose: number;
  rate_of_change: number;
  direction: string;
  rolling_2h_mean: number;
  rolling_2h_std: number;
  time_in_range_percent: number;
  forecasts: ForecastPoint[];
  active_alert: AlertInfo;
  top_explanations: FeatureAttribution[];
  total_carbs_last_2h: number;
  total_exercise_last_2h: number;
}

export interface StreamReading {
  timestamp: string;
  glucose: number;
  carbs: number;
  exercise_minutes: number;
  heart_rate: number;
}

export interface SimulationPayload {
  twin_state: DigitalTwinState;
  recent_history: StreamReading[];
  step_index: number;
  total_steps: number;
  is_playing: boolean;
  speed_multiplier: number;
}

export interface AblationMetric {
  model_key: string;
  display_name: string;
  horizon_minutes: number;
  mae: number;
  rmse: number;
  clarke_zone_a: number;
  clarke_zone_b: number;
  hypo_sensitivity: number;
  hyper_sensitivity: number;
}

export interface ClarkeGridPoint {
  reference: number;
  predicted: number;
  zone: string;
}

export interface PatientAblationSummary {
  patient_id: string;
  patient_name: string;
  hba1c: number;
  persistence_mae: number;
  fused_mae: number;
  mae_improvement_percent: number;
}

export interface BenchmarkReport {
  horizons: number[];
  models: AblationMetric[];
  clarke_sample_points: ClarkeGridPoint[];
  patient_breakdowns: PatientAblationSummary[];
  summary_findings: string[];
}
