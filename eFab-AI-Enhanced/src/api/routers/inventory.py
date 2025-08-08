"""Inventory router with real ERP data"""
from fastapi import APIRouter
from src.data.erp_loader import ERPDataLoader

router = APIRouter()
loader = ERPDataLoader()

@router.get("/current")
async def get_current_inventory():
    """Get current inventory from ERP"""
    data = loader.load_inventory()
    return {
        "total_items": len(data),
        "warehouses": data['warehouse'].unique().tolist() if 'warehouse' in data else [],
        "total_quantity": data['total_quantity'].sum() if 'total_quantity' in data else 0
    }

@router.get("/items")
async def get_inventory_items(limit: int = 100):
    """Get inventory items"""
    data = loader.load_inventory()
    if not data.empty:
        return data.head(limit).to_dict(orient='records')
    return []