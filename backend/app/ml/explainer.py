"""Clinical Feature Attribution and Prediction Explainer for GlucoTwin.
Translates mathematical feature contributions into intuitive, clinician-friendly
risk factors and mechanistic explanations.
"""

from typing import List, Dict, Any
from ..schemas.schemas import FeatureAttribution, PatientProfile


def explain_prediction(
    features: Dict[str, float],
    patient: PatientProfile,
    predicted_glucose: float,
    current_glucose: float
) -> List[FeatureAttribution]:
    """Generate top clinical feature attributions explaining the current forecast."""
    attributions: List[FeatureAttribution] = []
    delta = predicted_glucose - current_glucose
    v_5m = features.get("velocity_5m", 0.0)
    carb_decay = features.get("carb_decay_2h", 0.0)
    exercise_decay = features.get("exercise_decay_2h", 0.0)
    hour = features.get("sin_time_of_day", 0.0)
    
    # Factor 1: Rate of Change (Velocity)
    if abs(v_5m) >= 0.5:
        direction = "elevates" if v_5m > 0 else "lowers"
        rate_str = f"+{v_5m:.1f}" if v_5m > 0 else f"{v_5m:.1f}"
        attributions.append(FeatureAttribution(
            feature_name="velocity_5m",
            display_name=f"Glycemic Velocity ({rate_str} mg/dL/min)",
            impact_score=round(abs(v_5m) * 15.0, 1),
            direction=direction,
            clinical_explanation=f"Rapid glucose trajectory over recent 15 minutes drives strong near-term momentum."
        ))
        
    # Factor 2: Recent Carbohydrate Intake
    if carb_decay > 5.0:
        attributions.append(FeatureAttribution(
            feature_name="carb_decay_2h",
            display_name=f"Recent Meal Digestion ({carb_decay:.0f}g effective)",
            impact_score=round(min(carb_decay * 1.2, 45.0), 1),
            direction="elevates",
            clinical_explanation="Active carbohydrate absorption from recent meal intake elevating systemic blood glucose."
        ))
        
    # Factor 3: Recent Physical Activity
    if exercise_decay > 2.0:
        attributions.append(FeatureAttribution(
            feature_name="exercise_decay_2h",
            display_name="Physical Activity Influx",
            impact_score=round(min(exercise_decay * 1.5, 35.0), 1),
            direction="lowers",
            clinical_explanation="Non-insulin-mediated muscle glucose uptake actively exerting downward pressure."
        ))
        
    # Factor 4: Clinical Baseline & HbA1c
    if patient.hba1c >= 8.0:
        attributions.append(FeatureAttribution(
            feature_name="hba1c_baseline",
            display_name=f"Elevated Baseline HbA1c ({patient.hba1c}%)",
            impact_score=round((patient.hba1c - 7.0) * 8.0, 1),
            direction="elevates",
            clinical_explanation="Underlying chronic insulin resistance sustains higher steady-state fasting glucose equilibrium."
        ))
    elif patient.hba1c < 7.0:
        attributions.append(FeatureAttribution(
            feature_name="hba1c_baseline",
            display_name=f"Optimal Baseline HbA1c ({patient.hba1c}%)",
            impact_score=12.0,
            direction="lowers",
            clinical_explanation="Preserved beta-cell responsiveness aids rapid return to euglycemic target range."
        ))
        
    # Factor 5: Specific Medication Action
    for med in patient.medications:
        if "Sulfonylurea" in med.class_name and current_glucose < 100:
            attributions.append(FeatureAttribution(
                feature_name="med_sulfonylurea",
                display_name=f"{med.name} Activity",
                impact_score=18.0,
                direction="lowers",
                clinical_explanation="Secretagogue mechanism continues insulin secretion regardless of glycemic level, elevating hypoglycemia risk."
            ))
            break
        elif "SGLT2" in med.class_name and current_glucose > 180:
            attributions.append(FeatureAttribution(
                feature_name="med_sglt2",
                display_name=f"{med.name} Glucosuria",
                impact_score=14.0,
                direction="lowers",
                clinical_explanation="Renal glucose excretion dampens peak postprandial hyper excursions."
            ))
            break
            
    # Sort by impact score descending
    attributions.sort(key=lambda x: x.impact_score, reverse=True)
    return attributions[:4]
