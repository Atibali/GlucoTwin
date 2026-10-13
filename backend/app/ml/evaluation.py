"""Clinical and statistical evaluation metrics for CGM forecasting.
Includes MAE, RMSE, Excursion Event Sensitivity/Precision,
and full Clarke Error Grid Analysis (Zones A, B, C, D, E).
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from ..schemas.schemas import ClarkeGridPoint


def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def compute_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def compute_event_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float,
    is_hypo: bool = True
) -> Tuple[float, float]:
    """Calculate sensitivity (recall) and precision for threshold crossing events."""
    if is_hypo:
        actual_event = y_true < threshold
        pred_event = y_pred < threshold
    else:
        actual_event = y_true > threshold
        pred_event = y_pred > threshold
        
    tp = np.sum(actual_event & pred_event)
    fp = np.sum((~actual_event) & pred_event)
    fn = np.sum(actual_event & (~pred_event))
    
    sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 1.0
    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 1.0
    
    return sensitivity, precision


def assign_clarke_zone(ref: float, pred: float) -> str:
    """Classify a single (reference, predicted) glucose pair into Clarke Error Grid zone.
    Zones:
      'A': Clinically accurate, correct action
      'B': Benign errors, little or no clinical impact
      'C': Unnecessary treatment
      'D': Dangerous failure to detect hypo or hyper
      'E': Confusing hypoglycemia for hyperglycemia or vice-versa
    """
    # Zone A:
    # 1. Within 20% of reference
    # 2. Both ref and pred are in hypo range (<= 70)
    if (ref <= 70 and pred <= 70) or (abs(pred - ref) <= 0.20 * ref):
        return "A"
        
    # Zone E:
    # Severe failure: ref <= 70 and pred >= 180, OR ref >= 180 and pred <= 70
    if (ref <= 70 and pred >= 180) or (ref >= 180 and pred <= 70):
        return "E"
        
    # Zone D:
    # Failure to detect hypo: ref <= 70 and 70 < pred < 180
    # Failure to detect hyper: ref >= 240 and 70 < pred <= 180
    if (ref <= 70 and 70 < pred < 180) or (ref >= 240 and 70 < pred <= 180):
        return "D"
        
    # Zone C:
    # Overcorrection:
    # 1. ref between 70 and 290 and pred > ref + 110 (over-treatment)
    # 2. ref between 130 and 180 and pred < 70 (unnecessary hypo intervention)
    if (70 < ref < 290 and pred >= ref + 110) or (130 <= ref <= 180 and pred < 70):
        return "C"
        
    # Zone B:
    # All remaining errors are benign
    return "B"


def evaluate_clarke_grid(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sample_size: int = 400
) -> Tuple[Dict[str, float], List[ClarkeGridPoint]]:
    """Compute Clarke Error Grid distribution percentages and downsampled visualization points."""
    zones = [assign_clarke_zone(float(r), float(p)) for r, p in zip(y_true, y_pred)]
    total = len(zones)
    
    zone_counts = {z: zones.count(z) for z in ["A", "B", "C", "D", "E"]}
    zone_percentages = {z: round((count / total) * 100.0, 2) for z, count in zone_counts.items()}
    
    # Downsample points for efficient front-end charting
    indices = np.linspace(0, total - 1, min(sample_size, total), dtype=int)
    sample_points = [
        ClarkeGridPoint(
            reference=round(float(y_true[i]), 1),
            predicted=round(float(y_pred[i]), 1),
            zone=zones[i]
        )
        for i in indices
    ]
    
    return zone_percentages, sample_points
