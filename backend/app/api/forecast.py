"""Forecasting and Digital Twin control router."""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from ..schemas.schemas import DigitalTwinState, InjectIntervention
from ..engine.simulator_stream import get_or_create_simulation
from ..data.ehr_generator import get_patient_by_id

router = APIRouter(prefix="/forecast", tags=["Digital Twin & Forecast"])


@router.get("/{patient_id}/state")
def get_current_twin_state(patient_id: str) -> Dict[str, Any]:
    """Retrieve current digital twin state and recent stream for a patient."""
    p = get_patient_by_id(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found.")
    sim = get_or_create_simulation(patient_id)
    return sim.step()


@router.post("/{patient_id}/step")
def step_simulation(patient_id: str) -> Dict[str, Any]:
    """Advance the virtual patient simulation by one 5-minute interval."""
    sim = get_or_create_simulation(patient_id)
    return sim.step()


@router.post("/inject")
def inject_intervention(intervention: InjectIntervention):
    """Dynamically perturb the patient twin with a meal or exercise event."""
    sim = get_or_create_simulation(intervention.patient_id)
    sim.inject_event(intervention)
    return {"status": "ok", "message": f"Injected {intervention.event_type} event successfully."}


@router.post("/{patient_id}/control")
def update_control(
    patient_id: str,
    action: str = Body(..., embed=True),
    speed: float = Body(5.0, embed=True)
):
    """Update replay speed or play/pause state."""
    sim = get_or_create_simulation(patient_id)
    if action == "play":
        sim.set_playing(True)
    elif action == "pause":
        sim.set_playing(False)
    elif action == "speed":
        sim.set_speed(speed)
    return {
        "status": "ok",
        "is_playing": sim.is_playing,
        "speed_multiplier": sim.speed_multiplier
    }
