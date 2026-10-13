"""Tests for Machine Learning pipeline, feature extraction, and Clarke grid."""

import pytest
import numpy as np
import pandas as pd
from app.data.ehr_generator import get_patient_by_id
from app.data.dataset_loader import get_patient_stream
from app.ml.features import build_feature_dataset, compute_rolling_features_from_buffer
from app.ml.models import PersistenceModel, GlucoTwinForecaster
from app.ml.evaluation import assign_clarke_zone, evaluate_clarke_grid, compute_mae


def test_clarke_zone_assignment():
    # Accurate: within 20%
    assert assign_clarke_zone(100.0, 105.0) == "A"
    assert assign_clarke_zone(100.0, 119.0) == "A"
    # Hypo agreement
    assert assign_clarke_zone(60.0, 65.0) == "A"
    # Benign error: Zone B
    assert assign_clarke_zone(100.0, 130.0) == "B"
    # Extreme error: Zone E
    assert assign_clarke_zone(60.0, 220.0) == "E"
    assert assign_clarke_zone(220.0, 50.0) == "E"


def test_chronological_feature_dataset():
    patient = get_patient_by_id("PT-103")
    assert patient is not None
    df = get_patient_stream("PT-103", num_days=3)
    
    X_df, y_dict = build_feature_dataset(df, patient, horizons_steps={30: 6})
    
    assert len(X_df) > 0
    assert 30 in y_dict
    assert len(X_df) == len(y_dict[30])
    
    # Feature columns check
    assert "glucose_current" in X_df.columns
    assert "velocity_5m" in X_df.columns
    assert "hba1c" in X_df.columns
    assert "carb_decay_2h" in X_df.columns
    assert not X_df.isna().any().any()


def test_persistence_baseline():
    model = PersistenceModel()
    dummy_X = pd.DataFrame({"glucose_current": [120.0, 150.0, 90.0]})
    preds = model.predict(dummy_X, horizon_minutes=30)
    assert np.array_equal(preds, np.array([120.0, 150.0, 90.0]))
