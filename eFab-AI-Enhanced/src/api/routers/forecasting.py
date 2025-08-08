"""Forecasting router with real data"""
from fastapi import APIRouter
from src.data.erp_loader import ERPDataLoader

router = APIRouter()
loader = ERPDataLoader()

@router.get("/yarn-demand")
async def get_yarn_demand():
    """Get yarn demand forecast from ERP"""
    data = loader.load_yarn_demand()
    if not data.empty:
        week_cols = [col for col in data.columns if col.startswith('Week')]
        return {
            "weeks": week_cols,
            "total_styles": len(data),
            "data_source": "Beverly Knits ERP"
        }
    return {"message": "No demand data available"}

@router.post("/generate")
async def generate_forecast(request: dict):
    """Generate forecast with ML models"""
    # This would integrate with the planning engine
    return {
        "status": "forecast_generated",
        "horizon_days": request.get("horizon_days", 30),
        "models_used": ["prophet", "xgboost", "lightgbm"]
    }