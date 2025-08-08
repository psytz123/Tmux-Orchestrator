"""
Enhanced Planning Engine with Real ERP Data Integration
"""
import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.engine.planning.engine import PlanningEngine, PlanningRequest
from src.data.erp_loader import ERPDataLoader

logger = logging.getLogger(__name__)


class RealDataPlanningEngine(PlanningEngine):
    """Planning engine enhanced with real ERP data"""
    
    def __init__(self):
        super().__init__()
        self.erp_loader = ERPDataLoader()
        self.erp_data = None
        
    async def execute_planning(self, request: PlanningRequest) -> Dict[str, Any]:
        """Execute planning with real ERP data"""
        # Load real ERP data
        logger.info("Loading real ERP data from Beverly Knits system...")
        self.erp_data = self.erp_loader.load_all_data()
        
        # Log data statistics
        logger.info(f"Loaded inventory: {len(self.erp_data['inventory'])} records")
        logger.info(f"Loaded sales orders: {len(self.erp_data['sales_orders'])} records")
        logger.info(f"Loaded yarn demand: {len(self.erp_data['yarn_demand'])} records")
        
        # Execute planning with real data
        return await super().execute_planning(request)
    
    def _prepare_phase_input(
        self,
        phase_number: int,
        request: PlanningRequest,
        previous_output: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Prepare phase input with real ERP data"""
        base_input = super()._prepare_phase_input(phase_number, request, previous_output)
        
        # Enhance with real ERP data
        if self.erp_data:
            planning_data = self.erp_loader.get_planning_data()
            
            if phase_number == 1:  # Forecast Unification
                base_input["historical_demand"] = planning_data["demand_forecast"]
                base_input["current_orders"] = planning_data["sales_orders"]
                
            elif phase_number == 2:  # BOM Explosion
                base_input["inventory_levels"] = planning_data["current_inventory"]
                
            elif phase_number == 3:  # Inventory Netting
                base_input["current_inventory"] = planning_data["current_inventory"]
                
            elif phase_number == 4:  # Procurement Optimization
                base_input["lead_times"] = planning_data["lead_times"]
                
            elif phase_number == 5:  # Supplier Selection
                base_input["suppliers"] = planning_data["supplier_info"]
        
        return base_input


class RealDataForecastUnification:
    """Forecast unification with real yarn demand data"""
    
    def __init__(self, erp_data: Dict[str, Any]):
        self.erp_data = erp_data
        
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute forecast with real data"""
        logger.info("Executing Forecast Unification with real ERP data")
        
        yarn_demand = self.erp_data.get('yarn_demand', pd.DataFrame())
        sales_orders = self.erp_data.get('sales_orders', pd.DataFrame())
        
        if yarn_demand.empty:
            logger.warning("No yarn demand data available")
            return self._generate_fallback_forecast(input_data)
        
        # Extract weekly demand from real data
        week_columns = [col for col in yarn_demand.columns if col.startswith('Week')]
        
        if not week_columns:
            return self._generate_fallback_forecast(input_data)
        
        # Calculate total demand by week
        weekly_totals = {}
        for week in week_columns:
            weekly_totals[week] = yarn_demand[week].sum()
        
        # Generate forecast based on real demand patterns
        forecast_values = list(weekly_totals.values())
        
        # Apply ML models to enhance forecast
        enhanced_forecast = self._apply_ml_models(forecast_values)
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(yarn_demand, sales_orders)
        
        return {
            "forecast_type": "real_data",
            "weekly_demand": weekly_totals,
            "enhanced_forecast": enhanced_forecast,
            "confidence": confidence,
            "total_demand": sum(forecast_values),
            "average_weekly_demand": np.mean(forecast_values),
            "peak_week": max(weekly_totals, key=weekly_totals.get),
            "data_source": "Beverly Knits ERP"
        }
    
    def _apply_ml_models(self, historical_values: List[float]) -> List[float]:
        """Apply ML models to enhance forecast"""
        # Simplified ML enhancement - in production would use trained models
        values = np.array(historical_values)
        
        # Apply smoothing
        smoothed = pd.Series(values).rolling(window=3, min_periods=1).mean().values
        
        # Add trend adjustment
        if len(values) > 1:
            trend = (values[-1] - values[0]) / len(values)
            for i in range(len(smoothed)):
                smoothed[i] += trend * i * 0.1
        
        return smoothed.tolist()
    
    def _calculate_confidence(self, yarn_demand: pd.DataFrame, sales_orders: pd.DataFrame) -> float:
        """Calculate forecast confidence based on data quality"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data availability
        if not yarn_demand.empty:
            confidence += 0.2
        
        if not sales_orders.empty:
            confidence += 0.15
        
        # Check data completeness
        if not yarn_demand.empty:
            completeness = yarn_demand.notna().sum().sum() / yarn_demand.size
            confidence += completeness * 0.15
        
        return min(1.0, confidence)
    
    def _generate_fallback_forecast(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback forecast when real data is unavailable"""
        horizon_days = input_data.get("horizon_days", 30)
        
        # Simple forecast generation
        daily_demand = np.random.normal(100, 20, horizon_days)
        
        return {
            "forecast_type": "fallback",
            "daily_demand": daily_demand.tolist(),
            "confidence": 0.5,
            "total_demand": daily_demand.sum(),
            "average_daily_demand": daily_demand.mean(),
            "data_source": "Generated"
        }


class RealDataInventoryNetting:
    """Inventory netting with real Beverly Knits inventory data"""
    
    def __init__(self, erp_data: Dict[str, Any]):
        self.erp_data = erp_data
        
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute inventory netting with real data"""
        logger.info("Executing Inventory Netting with real ERP data")
        
        inventory = self.erp_data.get('inventory', pd.DataFrame())
        yarn_demand = self.erp_data.get('yarn_demand', pd.DataFrame())
        
        if inventory.empty:
            logger.warning("No inventory data available")
            return self._generate_fallback_netting(input_data)
        
        # Calculate net requirements
        net_requirements = []
        stockout_risks = []
        
        # Group inventory by style/material
        if 'style_number' in inventory.columns:
            grouped = inventory.groupby('style_number').agg({
                'total_quantity': 'sum',
                'warehouse': 'count'
            }).reset_index()
            
            for _, item in grouped.iterrows():
                style = item['style_number']
                current_stock = item['total_quantity']
                
                # Get demand for this style
                demand = 0
                if not yarn_demand.empty and 'Style' in yarn_demand.columns:
                    style_demand = yarn_demand[yarn_demand['Style'] == style]
                    if not style_demand.empty:
                        week_cols = [col for col in yarn_demand.columns if col.startswith('Week')]
                        demand = style_demand[week_cols].sum().sum()
                
                net_requirement = max(0, demand - current_stock)
                
                net_requirements.append({
                    "material": style,
                    "current_stock": current_stock,
                    "demand": demand,
                    "net_requirement": net_requirement,
                    "warehouses": item['warehouse']
                })
                
                if net_requirement > 0:
                    stockout_risks.append(style)
        
        # Calculate utilization metrics
        total_stock = inventory['total_quantity'].sum() if 'total_quantity' in inventory else 0
        total_demand = yarn_demand[[col for col in yarn_demand.columns if col.startswith('Week')]].sum().sum() if not yarn_demand.empty else 0
        
        utilization_rate = min(1.0, total_stock / total_demand) if total_demand > 0 else 0
        
        return {
            "net_requirements": net_requirements[:20],  # Top 20 items
            "stockout_risks": stockout_risks[:10],  # Top 10 risks
            "total_inventory": total_stock,
            "total_demand": total_demand,
            "utilization_rate": utilization_rate,
            "inventory_health": self._assess_inventory_health(utilization_rate, len(stockout_risks)),
            "warehouse_distribution": self._get_warehouse_distribution(inventory),
            "data_source": "Beverly Knits Inventory System"
        }
    
    def _assess_inventory_health(self, utilization: float, risks: int) -> str:
        """Assess overall inventory health"""
        if utilization < 0.5 or risks > 10:
            return "critical"
        elif utilization < 0.7 or risks > 5:
            return "warning"
        else:
            return "healthy"
    
    def _get_warehouse_distribution(self, inventory: pd.DataFrame) -> Dict[str, float]:
        """Get inventory distribution across warehouses"""
        if inventory.empty or 'warehouse' not in inventory or 'total_quantity' not in inventory:
            return {}
        
        distribution = inventory.groupby('warehouse')['total_quantity'].sum()
        return distribution.to_dict()
    
    def _generate_fallback_netting(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback netting when real data is unavailable"""
        return {
            "net_requirements": [],
            "stockout_risks": [],
            "total_inventory": 0,
            "total_demand": 0,
            "utilization_rate": 0,
            "inventory_health": "unknown",
            "data_source": "No data available"
        }