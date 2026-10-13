"""Tests for T2D Physiological Simulator."""

import pytest
import numpy as np
from datetime import datetime
from app.data.ehr_generator import get_patient_by_id
from app.data.t2d_simulator import T2DPhysiologicalSimulator


def test_t2d_simulator_trajectory():
    patient = get_patient_by_id("PT-101")
    assert patient is not None
    
    simulator = T2DPhysiologicalSimulator(patient=patient, random_seed=123)
    start_dt = datetime(2026, 10, 1, 0, 0, 0)
    df = simulator.generate_trajectory(start_date=start_dt, num_days=2, interval_minutes=5)
    
    # 2 days at 5-min intervals = 2 * 24 * 12 = 576 steps
    assert len(df) == 576
    assert "glucose" in df.columns
    assert "carbs" in df.columns
    assert "exercise_minutes" in df.columns
    assert "heart_rate" in df.columns
    
    # Biological plausibility assertions
    assert df["glucose"].min() >= 40.0, "Glucose should not drop below biological floor (40 mg/dL)"
    assert df["glucose"].max() <= 400.0, "Glucose should not exceed biological ceiling (400 mg/dL)"
    assert not df["glucose"].isna().any(), "No NaN values allowed in simulated trajectory"
    assert df["heart_rate"].min() >= 45.0
    assert df["heart_rate"].max() <= 190.0


def test_exercise_responsive_archetype():
    patient = get_patient_by_id("PT-106")  # Active patient
    assert patient is not None
    simulator = T2DPhysiologicalSimulator(patient=patient, random_seed=42)
    df = simulator.generate_trajectory(start_date=datetime(2026, 10, 1), num_days=1)
    
    # Check that exercise events were scheduled
    assert df["exercise_minutes"].sum() > 0
