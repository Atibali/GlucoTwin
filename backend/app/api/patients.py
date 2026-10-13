"""Patients API router."""

from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.schemas import PatientProfile
from ..data.ehr_generator import get_all_patients, get_patient_by_id
from ..data.dataset_loader import get_patient_stream

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("", response_model=List[PatientProfile])
def list_patients():
    """Retrieve all patient profiles in the synthetic EHR cohort."""
    return get_all_patients()


@router.get("/{patient_id}", response_model=PatientProfile)
def get_patient(patient_id: str):
    """Retrieve detailed clinical profile for a specific patient."""
    p = get_patient_by_id(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")
    return p


@router.get("/{patient_id}/stream")
def get_patient_raw_stream(patient_id: str, days: int = 3):
    """Retrieve recent raw CGM readings for visualization."""
    p = get_patient_by_id(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")
    df = get_patient_stream(patient_id, num_days=days)
    return df.to_dict(orient="records")
