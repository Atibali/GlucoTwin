"""FastAPI application entrypoint for GlucoTwin India."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .api import patients, forecast, ablation, websocket
from .ml.models import GlucoTwinForecaster
from .data.ehr_generator import get_all_patients
from .data.dataset_loader import get_patient_stream
from .ml.features import build_feature_dataset
from .engine.simulator_stream import _SIMULATION_REGISTRY, SimulationController
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("glucotwin")

# Global pre-trained forecaster instance
GLOBAL_FORECASTER: GlucoTwinForecaster = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up and pre-train the XGBoost forecaster on launch."""
    global GLOBAL_FORECASTER
    logger.info("Initializing GlucoTwin ML engine and warming up forecasters...")
    
    try:
        cohort = get_all_patients()
        horizons = [30, 60, 120]
        
        X_train_list = []
        y_train_dict = {h: [] for h in horizons}
        
        # Train on first 4 patients (7 days) for super fast startup
        for p in cohort[:4]:
            df = get_patient_stream(p.patient_id, num_days=7)
            X_df, y_dict = build_feature_dataset(df, p)
            # Use first 70% chronologically
            split_idx = int(len(X_df) * 0.70)
            X_train_list.append(X_df.iloc[:split_idx])
            for h in horizons:
                y_train_dict[h].append(y_dict[h][:split_idx])
                
        X_all = pd.concat(X_train_list, ignore_index=True)
        y_all = {h: np.concatenate(y_train_dict[h]) for h in horizons}
        
        forecaster = GlucoTwinForecaster(feature_mode="fused")
        forecaster.fit(X_all, y_all)
        GLOBAL_FORECASTER = forecaster
        
        # Pre-initialize simulations with the trained forecaster
        for p in cohort:
            _SIMULATION_REGISTRY[p.patient_id] = SimulationController(
                patient_id=p.patient_id,
                forecaster=GLOBAL_FORECASTER
            )
        logger.info("GlucoTwin models pre-trained and patient twins successfully initialized!")
    except Exception as e:
        logger.error(f"Error during ML warmup: {e}")
        
    yield
    logger.info("GlucoTwin backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personalized Type 2 Diabetes Digital Twin fusing CGM sensor data with longitudinal EHR records.",
    lifespan=lifespan
)

# Enable CORS for local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(patients.router, prefix=settings.API_V1_STR)
app.include_router(forecast.router, prefix=settings.API_V1_STR)
app.include_router(ablation.router, prefix=settings.API_V1_STR)
app.include_router(websocket.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "description": "Virtual patient Digital Twin API for Type 2 Diabetes glucose forecasting and early warnings.",
        "endpoints": {
            "patients": f"{settings.API_V1_STR}/patients",
            "forecast": f"{settings.API_V1_STR}/forecast",
            "ablation": f"{settings.API_V1_STR}/ablation/results",
            "websocket_stream": f"{settings.API_V1_STR}/ws/stream/{{patient_id}}",
            "docs": "/docs",
        }
    }
