"""Physiological Type 2 Diabetes CGM Simulator.
Simulates multi-day continuous glucose monitoring (CGM) time series
based on two-compartment postprandial glucose-insulin dynamics,
hepatic glucose production, exercise effects, diurnal rhythms,
and sensor autoregressive noise.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional
from ..schemas.schemas import PatientProfile, CGMReading


class T2DPhysiologicalSimulator:
    def __init__(self, patient: PatientProfile, random_seed: int = 42):
        self.patient = patient
        self.rng = np.random.default_rng(random_seed + hash(patient.patient_id) % 10000)
        
        # Patient specific physiological constants based on EHR
        # Insulin resistance factor scale based on BMI and HbA1c
        self.resistance_factor = 1.0 + (patient.bmi - 23.0) * 0.04 + (patient.hba1c - 6.0) * 0.15
        self.resistance_factor = max(0.8, min(self.resistance_factor, 2.5))
        
        # Basal target equilibrium (mg/dL)
        self.basal_glucose = patient.baseline_fasting_glucose
        
        # Check medication classes
        self.has_sulfonylurea = any("Sulfonylurea" in m.class_name for m in patient.medications)
        self.has_sglt2 = any("SGLT2" in m.class_name for m in patient.medications)
        self.has_insulin = any("Insulin" in m.class_name for m in patient.medications)
        
        # Clearance rate per 5-min step (fraction towards basal)
        # SGLT2i increases clearance; high resistance reduces clearance
        base_clearance = 0.045 / self.resistance_factor
        if self.has_sglt2:
            base_clearance *= 1.2
        self.clearance_rate = base_clearance

    def _get_daily_schedule(self, day_date: datetime) -> List[Dict[str, Any]]:
        """Generate meal and exercise events for a single day."""
        events = []
        
        # Breakfast: 08:00 - 09:00
        b_time = day_date.replace(hour=8, minute=self.rng.integers(15, 45), second=0)
        b_carbs = float(self.rng.normal(45, 10))
        events.append({"time": b_time, "type": "meal", "carbs": max(20.0, b_carbs), "exercise": 0.0})
        
        # Lunch: 13:00 - 14:00
        l_time = day_date.replace(hour=13, minute=self.rng.integers(15, 45), second=0)
        l_carbs = float(self.rng.normal(65, 15))
        events.append({"time": l_time, "type": "meal", "carbs": max(30.0, l_carbs), "exercise": 0.0})
        
        # Afternoon snack: 17:00
        if self.rng.random() > 0.3:
            s_time = day_date.replace(hour=17, minute=self.rng.integers(0, 30), second=0)
            s_carbs = float(self.rng.normal(25, 8))
            events.append({"time": s_time, "type": "meal", "carbs": max(10.0, s_carbs), "exercise": 0.0})
            
        # Dinner: 20:00 - 21:15
        d_time = day_date.replace(hour=20, minute=self.rng.integers(15, 45), second=0)
        d_carbs = float(self.rng.normal(70, 18))
        events.append({"time": d_time, "type": "meal", "carbs": max(35.0, d_carbs), "exercise": 0.0})
        
        # Physical activity (e.g. morning walk or evening exercise)
        if self.patient.patient_id == "PT-106":  # Active archetype
            ex_time = day_date.replace(hour=18, minute=30, second=0)
            events.append({"time": ex_time, "type": "exercise", "carbs": 0.0, "exercise": 45.0})
        elif self.rng.random() > 0.5:
            ex_time = day_date.replace(hour=self.rng.choice([7, 18]), minute=self.rng.integers(0, 30), second=0)
            ex_dur = float(self.rng.normal(30, 8))
            events.append({"time": ex_time, "type": "exercise", "carbs": 0.0, "exercise": max(15.0, ex_dur)})
            
        return events

    def generate_trajectory(
        self,
        start_date: datetime,
        num_days: int = 14,
        interval_minutes: int = 5
    ) -> pd.DataFrame:
        """Simulate a continuous multi-day CGM trajectory at 5-minute sampling intervals."""
        total_steps = int((num_days * 24 * 60) / interval_minutes)
        timestamps = [start_date + timedelta(minutes=i * interval_minutes) for i in range(total_steps)]
        
        # Collect all events for all days
        all_events = []
        for d in range(num_days + 1):
            cur_day = (start_date + timedelta(days=d)).replace(hour=0, minute=0, second=0)
            all_events.extend(self._get_daily_schedule(cur_day))
            
        # Event lookup by timestamp bucket (5-minute resolution)
        carb_inputs = np.zeros(total_steps)
        exercise_inputs = np.zeros(total_steps)
        
        for ev in all_events:
            idx = int((ev["time"] - start_date).total_seconds() / (interval_minutes * 60))
            if 0 <= idx < total_steps:
                carb_inputs[idx] += ev["carbs"]
                exercise_inputs[idx] += ev["exercise"]
                
        # State variables for two-compartment gut absorption
        gut_carb = 0.0
        active_glucose_influx = 0.0
        
        # Exercise active effect buffer
        active_exercise_effect = 0.0
        
        # CGM initial glucose
        g = self.basal_glucose + self.rng.normal(0, 5)
        
        glucose_history = np.zeros(total_steps)
        hr_history = np.zeros(total_steps)
        
        sensor_noise_ar = 0.0  # AR(1) sensor noise
        
        for t in range(total_steps):
            cur_time = timestamps[t]
            hour_float = cur_time.hour + cur_time.minute / 60.0
            
            # Diurnal Circadian variation: Dawn phenomenon (4am - 8am peak)
            dawn_effect = 12.0 * np.exp(-((hour_float - 6.5) ** 2) / (2 * (1.8 ** 2)))
            
            # Nocturnal dip (1am - 4am)
            night_effect = -8.0 * np.exp(-((hour_float - 2.5) ** 2) / (2 * (1.5 ** 2)))
            
            # Sulfonylurea late-afternoon dip effect (PT-102 or sulfonylurea patients)
            su_dip = 0.0
            if self.has_sulfonylurea:
                su_dip = -15.0 * np.exp(-((hour_float - 16.5) ** 2) / (2 * (1.5 ** 2)))
                
            dynamic_basal = self.basal_glucose + dawn_effect + night_effect + su_dip
            
            # Gut absorption kinetics:
            # Meal ingestion dumps into gut compartment
            if carb_inputs[t] > 0:
                gut_carb += carb_inputs[t] * 2.8 * self.resistance_factor  # mg/dL equivalent
                
            # Gut clearance into blood stream (rate ~0.08 per 5 min)
            absorption = gut_carb * 0.08
            gut_carb -= absorption
            active_glucose_influx = absorption
            
            # Exercise kinetics:
            if exercise_inputs[t] > 0:
                active_exercise_effect += exercise_inputs[t] * 1.5  # Glucose drop potential
                
            exercise_burn = active_exercise_effect * 0.10
            active_exercise_effect -= exercise_burn
            
            # Equilibrium pull towards dynamic basal
            delta_eq = -self.clearance_rate * (g - dynamic_basal)
            
            # Net glucose rate of change
            dg = delta_eq + active_glucose_influx - exercise_burn
            
            # Integration
            g = g + dg
            
            # Physiological boundaries
            g = max(40.0, min(g, 380.0))
            
            # Sensor autoregressive noise (Dexcom MARD emulation)
            sensor_noise_ar = 0.75 * sensor_noise_ar + self.rng.normal(0, 1.8)
            measured_g = g + sensor_noise_ar
            measured_g = max(40.0, min(measured_g, 400.0))
            
            # Heart rate estimation: basal 70 bpm + exercise surge + postprandial bump
            base_hr = 72.0
            hr_surge = exercise_burn * 3.5
            postprandial_hr = (active_glucose_influx > 0.5) * 5.0
            hr = base_hr + hr_surge + postprandial_hr + self.rng.normal(0, 2.5)
            
            glucose_history[t] = round(measured_g, 1)
            hr_history[t] = round(hr, 1)
            
        df = pd.DataFrame({
            "timestamp": [ts.isoformat() for ts in timestamps],
            "glucose": glucose_history,
            "carbs": carb_inputs,
            "exercise_minutes": exercise_inputs,
            "heart_rate": hr_history,
            "patient_id": self.patient.patient_id,
        })
        
        return df


def simulate_patient_cgm(
    patient: PatientProfile,
    num_days: int = 14,
    start_date: Optional[datetime] = None
) -> pd.DataFrame:
    """Generate simulated CGM dataset for a given patient profile."""
    if start_date is None:
        start_date = datetime(2026, 10, 1, 0, 0, 0)
    simulator = T2DPhysiologicalSimulator(patient=patient)
    return simulator.generate_trajectory(start_date=start_date, num_days=num_days)
