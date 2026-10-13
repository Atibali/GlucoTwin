"""GlucoTwin configuration module."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "GlucoTwin India - Personalized T2D Digital Twin"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Clinical thresholds (mg/dL)
    HYPOGLYCEMIA_THRESHOLD: float = 70.0
    SEVERE_HYPO_THRESHOLD: float = 54.0
    HYPERGLYCEMIA_THRESHOLD: float = 180.0
    SEVERE_HYPER_THRESHOLD: float = 250.0
    
    # Forecasting Horizons (in minutes and 5-min steps)
    INTERVAL_MINUTES: int = 5
    HORIZONS_MINUTES: List[int] = [30, 60, 120]
    HORIZONS_STEPS: List[int] = [6, 12, 24]  # 30m=6, 60m=12, 120m=24
    
    # History buffer length required for feature extraction (in steps)
    HISTORY_STEPS: int = 24  # 2 hours of 5-min readings
    
    # Uncertainty interval confidence (default 80%: 10th to 90th percentile)
    CONFIDENCE_LEVEL: float = 0.80

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
