import os
import json
from fastapi import APIRouter
from typing import Optional
from ..schemas.schemas import BenchmarkReport
from ..ml.ablation import run_full_cohort_benchmark

router = APIRouter(prefix="/ablation", tags=["Ablation Benchmark"])

_CACHED_REPORT: Optional[BenchmarkReport] = None
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "benchmark_cache.json")


@router.get("/results", response_model=BenchmarkReport)
def get_ablation_results():
    """Retrieve full chronological ablation study and Clarke Error Grid report."""
    global _CACHED_REPORT
    if _CACHED_REPORT is not None:
        return _CACHED_REPORT
        
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                _CACHED_REPORT = BenchmarkReport.model_validate(data)
                return _CACHED_REPORT
        except Exception:
            pass
            
    _CACHED_REPORT = run_full_cohort_benchmark()
    return _CACHED_REPORT
