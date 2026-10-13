#!/usr/bin/env bash
echo "==========================================================================="
echo "           GlucoTwin India - Digital Twin Challenge 2026"
echo "  Personalized T2D Glucose Forecasting & Early Warning Digital Twin"
echo "==========================================================================="
echo ""

echo "[1/3] Ensuring precomputed benchmark cache exists..."
python backend/train_and_evaluate.py

echo ""
echo "[2/3] Launching FastAPI Backend on http://localhost:8003 ..."
(cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload) &
BACKEND_PID=$!

echo ""
echo "[3/3] Launching React Vite Frontend on http://localhost:5173 ..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM EXIT
wait
