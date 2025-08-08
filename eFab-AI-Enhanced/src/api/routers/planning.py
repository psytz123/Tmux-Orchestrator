"""
Planning API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
import uuid

from src.engine.planning.engine import PlanningEngine, PlanningRequest
from src.engine.planning.real_data_engine import RealDataPlanningEngine
from src.database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# Initialize planning engine with real data support
planning_engine = RealDataPlanningEngine()


@router.post("/runs")
async def create_planning_run(
    request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create and execute a new planning run"""
    try:
        # Create planning request
        planning_request = PlanningRequest(
            name=request.get("name", f"Plan-{datetime.now().strftime('%Y%m%d-%H%M')}"),
            horizon_days=request.get("horizon_days", 30),
            algorithm=request.get("algorithm", "mixed_integer"),
            objective=request.get("objective", "minimize_cost"),
            parameters=request.get("parameters", {}),
            user_id=request.get("user_id")
        )
        
        # Execute planning in background
        run_id = str(uuid.uuid4())
        background_tasks.add_task(
            planning_engine.execute_planning,
            planning_request
        )
        
        return {
            "planning_run_id": run_id,
            "status": "started",
            "message": "Planning run initiated successfully",
            "estimated_time": "5-10 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs")
async def list_planning_runs(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """List all planning runs"""
    # TODO: Implement database query
    return [
        {
            "id": str(uuid.uuid4()),
            "name": f"Planning Run {i+1}",
            "status": "completed" if i < 5 else "running",
            "created_at": datetime.now().isoformat(),
            "horizon_days": 30
        }
        for i in range(limit)
    ]


@router.get("/runs/{run_id}")
async def get_planning_run(
    run_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get details of a specific planning run"""
    # TODO: Implement database query
    return {
        "id": run_id,
        "name": "Q1 2024 Planning",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "execution_time_seconds": 285.3,
        "total_cost": 125000.50,
        "optimization_score": 87.5,
        "phases": [
            {"name": "Forecast Unification", "status": "completed"},
            {"name": "BOM Explosion", "status": "completed"},
            {"name": "Inventory Netting", "status": "completed"},
            {"name": "Procurement Optimization", "status": "completed"},
            {"name": "Supplier Selection", "status": "completed"},
            {"name": "Output Generation", "status": "completed"}
        ]
    }


@router.get("/runs/{run_id}/phases")
async def get_planning_phases(
    run_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get phase details for a planning run"""
    phases = [
        "Forecast Unification",
        "BOM Explosion",
        "Inventory Netting",
        "Procurement Optimization",
        "Supplier Selection",
        "Output Generation"
    ]
    
    return [
        {
            "phase_number": i + 1,
            "name": phase,
            "status": "completed",
            "execution_time": 45 + (i * 10),
            "output": {
                "status": "success",
                "records_processed": 1000 + (i * 500)
            }
        }
        for i, phase in enumerate(phases)
    ]


@router.post("/runs/{run_id}/cancel")
async def cancel_planning_run(
    run_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Cancel a running planning run"""
    # TODO: Implement cancellation logic
    return {
        "status": "cancelled",
        "message": f"Planning run {run_id} has been cancelled"
    }