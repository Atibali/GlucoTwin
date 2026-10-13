@echo off
echo ===========================================================================
echo            GlucoTwin India - Digital Twin Challenge 2026
echo   Personalized T2D Glucose Forecasting & Early Warning Digital Twin
echo ===========================================================================
echo.

echo [1/3] Ensuring precomputed benchmark cache exists...
python backend/train_and_evaluate.py

echo.
echo [2/3] Launching FastAPI Backend on http://localhost:8003 ...
start "GlucoTwin Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload"

echo.
echo [3/3] Launching React Vite Frontend on http://localhost:5173 ...
start "GlucoTwin Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===========================================================================
echo GlucoTwin is launching!
echo   • Clinician Dashboard:  http://localhost:5173
echo   • FastAPI Docs / REST:   http://localhost:8003/docs
echo   • WebSocket Stream:      ws://localhost:8003/api/ws/stream/{patient_id}
echo ===========================================================================
