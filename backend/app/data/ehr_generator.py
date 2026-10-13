"""Synthetic EHR Generator for GlucoTwin India.
Generates realistic clinical profiles for diverse Type 2 Diabetes archetypes,
matching standard FHIR / Synthea data elements.
"""

from typing import List, Dict, Optional
from ..schemas.schemas import PatientProfile, Medication


PATIENT_COHORT: List[PatientProfile] = [
    PatientProfile(
        patient_id="PT-101",
        name="Rajesh Patel",
        age=52,
        gender="Male",
        hba1c=7.4,
        bmi=27.2,
        duration_years=5.5,
        medications=[
            Medication(name="Metformin", dose="1000mg BID", class_name="Biguanide"),
            Medication(name="Sitagliptin", dose="100mg OD", class_name="DPP-4 Inhibitor"),
        ],
        baseline_fasting_glucose=132.0,
        baseline_cv=26.5,
        archetype_title="Moderate T2D on Dual Oral Therapy",
        clinical_notes="Typical postprandial glucose excursions following high-carb evening meals. Moderate insulin resistance.",
        target_range_min=70.0,
        target_range_max=180.0,
    ),
    PatientProfile(
        patient_id="PT-102",
        name="Sunita Sharma",
        age=61,
        gender="Female",
        hba1c=8.8,
        bmi=30.5,
        duration_years=9.0,
        medications=[
            Medication(name="Metformin", dose="1000mg BID", class_name="Biguanide"),
            Medication(name="Glimepiride", dose="2mg OD", class_name="Sulfonylurea"),
        ],
        baseline_fasting_glucose=168.0,
        baseline_cv=36.2,
        archetype_title="High Variability with Hypoglycemia Risk",
        clinical_notes="Elevated HbA1c with significant glycemic variability. Sulfonylurea therapy presents periodic late-afternoon reactive hypoglycemic dips.",
        target_range_min=70.0,
        target_range_max=180.0,
    ),
    PatientProfile(
        patient_id="PT-103",
        name="Anand Verma",
        age=44,
        gender="Male",
        hba1c=6.8,
        bmi=25.8,
        duration_years=2.0,
        medications=[
            Medication(name="Metformin", dose="500mg BID", class_name="Biguanide"),
        ],
        baseline_fasting_glucose=112.0,
        baseline_cv=19.4,
        archetype_title="Early-Stage T2D on Monotherapy",
        clinical_notes="Well-controlled baseline glycemia with lifestyle modifications. Highly predictable meal-response kinetics.",
        target_range_min=70.0,
        target_range_max=160.0,
    ),
    PatientProfile(
        patient_id="PT-104",
        name="Meera Nair",
        age=68,
        gender="Female",
        hba1c=8.2,
        bmi=28.1,
        duration_years=15.0,
        medications=[
            Medication(name="Insulin Glargine", dose="18 units QHS", class_name="Basal Insulin"),
            Medication(name="Empagliflozin", dose="10mg OD", class_name="SGLT2 Inhibitor"),
            Medication(name="Metformin", dose="850mg BID", class_name="Biguanide"),
        ],
        baseline_fasting_glucose=154.0,
        baseline_cv=34.0,
        archetype_title="Long-standing T2D on Basal Insulin & SGLT2i",
        clinical_notes="Significant beta-cell exhaustion. Impaired hypoglycemic awareness, vulnerable to nocturnal excursions.",
        target_range_min=70.0,
        target_range_max=180.0,
    ),
    PatientProfile(
        patient_id="PT-105",
        name="Vikram Sengupta",
        age=58,
        gender="Male",
        hba1c=9.3,
        bmi=32.4,
        duration_years=11.0,
        medications=[
            Medication(name="Metformin", dose="1000mg BID", class_name="Biguanide"),
            Medication(name="Vildagliptin", dose="50mg BID", class_name="DPP-4 Inhibitor"),
            Medication(name="Pioglitazone", dose="15mg OD", class_name="Thiazolidinedione"),
        ],
        baseline_fasting_glucose=185.0,
        baseline_cv=39.5,
        archetype_title="Severe Insulin Resistance & High Glycemic Excursions",
        clinical_notes="Marked visceral adiposity, severe insulin resistance, pronounced dawn phenomenon (morning fasting spikes > 200 mg/dL).",
        target_range_min=70.0,
        target_range_max=200.0,
    ),
    PatientProfile(
        patient_id="PT-106",
        name="Pooja Iyer",
        age=39,
        gender="Female",
        hba1c=6.5,
        bmi=23.8,
        duration_years=1.5,
        medications=[
            Medication(name="Metformin", dose="500mg OD", class_name="Biguanide"),
        ],
        baseline_fasting_glucose=105.0,
        baseline_cv=21.0,
        archetype_title="Active Lifestyle & Exercise-Responsive T2D",
        clinical_notes="High physical activity compliance. Displays rapid exercise-induced glucose drop during evening workouts.",
        target_range_min=70.0,
        target_range_max=160.0,
    ),
]


def get_all_patients() -> List[PatientProfile]:
    """Retrieve full synthetic EHR cohort."""
    return PATIENT_COHORT


def get_patient_by_id(patient_id: str) -> Optional[PatientProfile]:
    """Find patient by ID."""
    for p in PATIENT_COHORT:
        if p.patient_id == patient_id:
            return p
    return None
