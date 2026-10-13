"""Interactive Simulation Stream Manager for GlucoTwin India.
Coordinates live/accelerated replay of CGM sensor streams,
dynamic intervention injections (meals, exercise), and state publishing.
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable, Any
from ..schemas.schemas import PatientProfile, CGMReading, DigitalTwinState, InjectIntervention
from ..data.ehr_generator import get_patient_by_id
from ..data.dataset_loader import get_patient_stream
from .twin_engine import PatientDigitalTwin
from ..ml.models import GlucoTwinForecaster


class SimulationController:
    """Manages active streaming playback and user interactions for a patient."""
    
    def __init__(self, patient_id: str, forecaster: Optional[GlucoTwinForecaster] = None):
        self.patient_id = patient_id
        self.patient = get_patient_by_id(patient_id)
        if not self.patient:
            raise ValueError(f"Patient {patient_id} not found.")
            
        self.forecaster = forecaster
        self.stream_df = get_patient_stream(patient_id, num_days=14)
        self.twin = PatientDigitalTwin(self.patient, forecaster=self.forecaster)
        
        # Start at step 48 (4 hours into simulation to ensure warm buffer)
        self.current_step = 48
        self.is_playing = False
        self.speed_multiplier = 5.0  # 1x, 5x, 10x, 30x
        
        # Injected dynamic perturbation buffer
        self.injected_gut_carbs = 0.0
        self.injected_exercise_burn = 0.0
        
        # Initialize twin buffer with first 48 readings
        initial_readings = [
            CGMReading(
                timestamp=str(row["timestamp"]),
                glucose=float(row["glucose"]),
                carbs=float(row["carbs"]),
                exercise_minutes=float(row["exercise_minutes"]),
                heart_rate=float(row["heart_rate"])
            )
            for _, row in self.stream_df.iloc[:self.current_step].iterrows()
        ]
        self.twin.initialize_with_history(initial_readings)

    def step(self) -> Dict[str, Any]:
        """Advance simulation by 1 step (5 minutes)."""
        if self.current_step >= len(self.stream_df) - 1:
            self.current_step = 48  # Loop back if reached end
            
        self.current_step += 1
        row = self.stream_df.iloc[self.current_step].copy()
        
        # Apply any active injected interventions
        g_val = float(row["glucose"])
        c_val = float(row["carbs"])
        e_val = float(row["exercise_minutes"])
        
        if self.injected_gut_carbs > 0:
            absorption = self.injected_gut_carbs * 0.12
            self.injected_gut_carbs -= absorption
            g_val += absorption
            c_val += absorption / 2.0
            
        if self.injected_exercise_burn > 0:
            burn = self.injected_exercise_burn * 0.15
            self.injected_exercise_burn -= burn
            g_val -= burn
            e_val += burn
            
        g_val = float(np.clip(g_val, 40.0, 400.0))
        
        reading = CGMReading(
            timestamp=str(row["timestamp"]),
            glucose=round(g_val, 1),
            carbs=round(c_val, 1),
            exercise_minutes=round(e_val, 1),
            heart_rate=float(row["heart_rate"])
        )
        
        self.twin.ingest_reading(reading)
        state = self.twin.compute_state()
        
        # Recent history for charting (past 28 readings = 2h 20m)
        history_start = max(0, self.current_step - 28)
        recent_rows = self.stream_df.iloc[history_start:self.current_step + 1]
        
        history_list = [
            {
                "timestamp": str(r["timestamp"]),
                "glucose": float(r["glucose"]),
                "carbs": float(r["carbs"]),
                "exercise_minutes": float(r["exercise_minutes"]),
                "heart_rate": float(r["heart_rate"]),
            }
            for _, r in recent_rows.iterrows()
        ]
        # Ensure the last element matches our perturbed g_val
        if history_list:
            history_list[-1]["glucose"] = round(g_val, 1)
            history_list[-1]["carbs"] = round(c_val, 1)
            
        return {
            "twin_state": state.model_dump(),
            "recent_history": history_list,
            "step_index": self.current_step,
            "total_steps": len(self.stream_df),
            "is_playing": self.is_playing,
            "speed_multiplier": self.speed_multiplier,
        }

    def inject_event(self, intervention: InjectIntervention):
        """Simulate a meal or exercise event injected in real time."""
        if intervention.event_type == "meal" or intervention.carbs > 0:
            self.injected_gut_carbs += intervention.carbs * 2.5
        elif intervention.event_type == "exercise" or intervention.exercise_minutes > 0:
            self.injected_exercise_burn += intervention.exercise_minutes * 1.8

    def set_speed(self, speed: float):
        self.speed_multiplier = max(0.5, min(speed, 60.0))

    def set_playing(self, play: bool):
        self.is_playing = play


# Global simulation registry keyed by patient_id
_SIMULATION_REGISTRY: Dict[str, SimulationController] = {}


def get_or_create_simulation(
    patient_id: str,
    forecaster: Optional[GlucoTwinForecaster] = None
) -> SimulationController:
    if patient_id not in _SIMULATION_REGISTRY:
        _SIMULATION_REGISTRY[patient_id] = SimulationController(
            patient_id=patient_id,
            forecaster=forecaster
        )
    return _SIMULATION_REGISTRY[patient_id]
