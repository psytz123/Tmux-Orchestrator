"""Analytics router"""
from fastapi import APIRouter
from src.data.erp_loader import ERPDataLoader

router = APIRouter()
loader = ERPDataLoader()

@router.get("/summary")
async def get_analytics_summary():
    """Get analytics summary from ERP data"""
    data = loader.load_all_data()
    return data['summary']

@router.get("/kpis")
async def get_kpis():
    """Get key performance indicators"""
    data = loader.load_all_data()
    summary = data['summary']
    
    return {
        "inventory_value": summary.get("total_order_value", 0),
        "total_orders": summary.get("total_sales_orders", 0),
        "warehouses": len(summary.get("warehouses", [])),
        "critical_items": len(summary.get("critical_items", []))
    }