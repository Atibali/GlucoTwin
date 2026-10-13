"""Standalone training, chronological validation, and ablation benchmark script.
Evaluates Persistence Baseline vs. Sensor-Only vs. EHR-Only vs. Fused Twin
and outputs clinical performance metrics (MAE, RMSE, Clarke Error Grid Zones A-E, Sensitivity).
"""

import os
import sys
import json

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ml.ablation import run_full_cohort_benchmark


def main():
    print("=" * 75)
    print("  GlucoTwin India: Chronological Multi-Horizon Benchmark & Ablation Study")
    print("=" * 75)
    print("\nRunning evaluation across 6 diverse Type 2 Diabetes clinical archetypes...")
    
    report = run_full_cohort_benchmark()
    
    print("\n" + "-" * 75)
    print(f"{'Model':<32} | {'Horizon':<8} | {'MAE (mg/dL)':<12} | {'RMSE':<8} | {'Clarke A+B %':<12}")
    print("-" * 75)
    
    for m in report.models:
        ab_percent = m.clarke_zone_a + m.clarke_zone_b
        print(f"{m.display_name:<32} | {m.horizon_minutes} min    | {m.mae:<12.2f} | {m.rmse:<8.2f} | {ab_percent:<12.1f}%")
        
    print("-" * 75)
    print("\nPer-Patient 30-Minute Performance Improvement:")
    print(f"{'Patient ID':<12} | {'Name':<18} | {'HbA1c':<6} | {'Persist MAE':<12} | {'Fused MAE':<10} | {'Gain %':<8}")
    print("-" * 75)
    for p in report.patient_breakdowns:
        print(f"{p.patient_id:<12} | {p.patient_name:<18} | {p.hba1c:<6.1f} | {p.persistence_mae:<12.2f} | {p.fused_mae:<10.2f} | +{p.mae_improvement_percent:<6.1f}%")
        
    print("-" * 75)
    print("\nKey Clinical Evidence Findings:")
    for f in report.summary_findings:
        print(f"  • {f}")
        
    # Save cache for instant API consumption
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "data", "benchmark_cache.json")
    with open(cache_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2)
    print(f"\n[OK] Benchmark report saved to {cache_path}")


if __name__ == "__main__":
    main()
