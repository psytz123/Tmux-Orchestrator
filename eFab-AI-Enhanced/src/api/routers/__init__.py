"""API Routers"""
from .auth import router as auth_router
from .planning import router as planning_router
from .inventory import router as inventory_router
from .forecasting import router as forecasting_router
from .analytics import router as analytics_router

__all__ = [
    "auth_router",
    "planning_router", 
    "inventory_router",
    "forecasting_router",
    "analytics_router"
]