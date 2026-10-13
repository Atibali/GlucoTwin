"""Tests for Digital Twin Engine and Alert System."""

import pytest
from datetime import datetime, timedelta
from app.data.ehr_generator import get_patient_by_id
from app.schemas.schemas import CGMReading
from app.engine.twin_engine import PatientDigitalTwin


def test_twin_state_and_alerts():
    patient = get_patient_by_id("PT-101")
    twin = PatientDigitalTwin(patient=patient)
    
    # Ingest 30 synthetic readings
    base_time = datetime(2026, 10, 1, 12, 0, 0)
    for i in range(30):
        t = base_time + timedelta(minutes=i * 5)
        twin.ingest_reading(CGMReading(
            timestamp=t.isoformat(),
            glucose=125.0 + i * 0.5,
            carbs=0.0,
            exercise_minutes=0.0
        ))
        
    state = twin.compute_state()
    assert state.patient_id == "PT-101"
    assert state.current_glucose > 130.0
    assert len(state.forecasts) == 3
    assert state.forecasts[0].horizon_minutes == 30
    assert state.forecasts[1].horizon_minutes == 60
    assert state.forecasts[2].horizon_minutes == 120
    assert state.active_alert is not None
    assert state.rolling_2h_mean > 0


def test_twin_hypoglycemia_alert():
    patient = get_patient_by_id("PT-102")
    twin = PatientDigitalTwin(patient=patient)
    
    # Rapid downward slope to trigger hypo warning
    base_time = datetime(2026, 10, 1, 16, 0, 0)
    for i in range(25):
        t = base_time + timedelta(minutes=i * 5)
        # Drops rapidly from 110 to 65
        g = 110.0 - i * 2.0
        twin.ingest_reading(CGMReading(
            timestamp=t.isoformat(),
            glucose=max(55.0, g),
            carbs=0.0,
            exercise_minutes=0.0
        ))
        
    state = twin.compute_state()
    assert state.active_alert.is_active is True
    assert state.active_alert.excursion_type == "hypoglycemia"
