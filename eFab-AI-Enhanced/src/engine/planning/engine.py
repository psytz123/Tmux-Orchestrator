"""
6-Phase Planning Engine for eFab AI Enhanced
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid

from src.core.config import settings
from src.database.models.planning import PlanningRun, PlanningPhase, PlanningStatus
from src.engine.planning.phases import (
    ForecastUnification,
    BOMExplosion,
    InventoryNetting,
    ProcurementOptimization,
    SupplierSelection,
    OutputGeneration
)

logger = logging.getLogger(__name__)


@dataclass
class PlanningRequest:
    """Planning request data structure"""
    name: str
    horizon_days: int = 30
    algorithm: str = "mixed_integer"
    objective: str = "minimize_cost"
    parameters: Dict[str, Any] = None
    user_id: Optional[str] = None


class PlanningEngine:
    """
    Main planning engine orchestrating the 6-phase planning process
    
    Phases:
    1. Forecast Unification
    2. BOM Explosion
    3. Inventory Netting
    4. Procurement Optimization
    5. Supplier Selection
    6. Output Generation
    """
    
    def __init__(self):
        self.phases = [
            ForecastUnification(),
            BOMExplosion(),
            InventoryNetting(),
            ProcurementOptimization(),
            SupplierSelection(),
            OutputGeneration()
        ]
        self.current_run: Optional[PlanningRun] = None
        
    async def execute_planning(self, request: PlanningRequest) -> Dict[str, Any]:
        """
        Execute complete planning cycle
        """
        start_time = datetime.utcnow()
        
        try:
            # Initialize planning run
            self.current_run = await self._create_planning_run(request)
            logger.info(f"Started planning run: {self.current_run.id}")
            
            # Execute phases sequentially
            phase_results = {}
            previous_output = None
            
            for idx, phase in enumerate(self.phases, 1):
                phase_name = phase.__class__.__name__
                logger.info(f"Executing Phase {idx}: {phase_name}")
                
                # Create phase record
                phase_record = await self._create_phase_record(
                    phase_number=idx,
                    phase_name=phase_name
                )
                
                try:
                    # Execute phase
                    phase_input = self._prepare_phase_input(
                        phase_number=idx,
                        request=request,
                        previous_output=previous_output
                    )
                    
                    phase_output = await phase.execute(phase_input)
                    phase_results[phase_name] = phase_output
                    previous_output = phase_output
                    
                    # Update phase record
                    await self._update_phase_record(
                        phase_record,
                        PlanningStatus.COMPLETED,
                        output_data=phase_output
                    )
                    
                    logger.info(f"Completed Phase {idx}: {phase_name}")
                    
                except Exception as e:
                    logger.error(f"Failed Phase {idx}: {phase_name} - {str(e)}")
                    await self._update_phase_record(
                        phase_record,
                        PlanningStatus.FAILED,
                        error_message=str(e)
                    )
                    raise
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Generate final results
            results = await self._generate_results(phase_results, execution_time)
            
            # Update planning run status
            await self._update_planning_run(
                PlanningStatus.COMPLETED,
                results=results,
                execution_time=execution_time
            )
            
            logger.info(f"Planning run completed in {execution_time:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Planning run failed: {str(e)}")
            await self._update_planning_run(
                PlanningStatus.FAILED,
                error_message=str(e)
            )
            raise
    
    async def _create_planning_run(self, request: PlanningRequest) -> PlanningRun:
        """Create new planning run record"""
        planning_run = PlanningRun(
            id=uuid.uuid4(),
            name=request.name,
            status=PlanningStatus.PENDING,
            planning_horizon_days=request.horizon_days,
            optimization_algorithm=request.algorithm,
            objective_function=request.objective,
            parameters=request.parameters,
            created_by=request.user_id,
            started_at=datetime.utcnow()
        )
        # TODO: Save to database
        return planning_run
    
    async def _create_phase_record(self, phase_number: int, phase_name: str) -> PlanningPhase:
        """Create phase execution record"""
        phase = PlanningPhase(
            id=uuid.uuid4(),
            planning_run_id=self.current_run.id,
            phase_number=phase_number,
            phase_name=phase_name,
            status=PlanningStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        # TODO: Save to database
        return phase
    
    async def _update_phase_record(
        self,
        phase: PlanningPhase,
        status: PlanningStatus,
        output_data: Dict[str, Any] = None,
        error_message: str = None
    ):
        """Update phase execution record"""
        phase.status = status
        phase.completed_at = datetime.utcnow()
        phase.execution_time_seconds = (
            phase.completed_at - phase.started_at
        ).total_seconds()
        
        if output_data:
            phase.output_data = output_data
        if error_message:
            phase.error_message = error_message
        
        # TODO: Update in database
    
    async def _update_planning_run(
        self,
        status: PlanningStatus,
        results: Dict[str, Any] = None,
        execution_time: float = None,
        error_message: str = None
    ):
        """Update planning run record"""
        self.current_run.status = status
        self.current_run.completed_at = datetime.utcnow()
        
        if results:
            self.current_run.results = results
            self.current_run.total_cost = results.get("total_cost")
            self.current_run.total_units_planned = results.get("total_units")
            self.current_run.optimization_score = results.get("optimization_score")
        
        if execution_time:
            self.current_run.execution_time_seconds = execution_time
        
        if error_message:
            self.current_run.error_message = error_message
        
        # TODO: Update in database
    
    def _prepare_phase_input(
        self,
        phase_number: int,
        request: PlanningRequest,
        previous_output: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare input for phase execution"""
        base_input = {
            "planning_run_id": str(self.current_run.id),
            "horizon_days": request.horizon_days,
            "parameters": request.parameters or {}
        }
        
        if previous_output:
            base_input["previous_phase_output"] = previous_output
        
        # Phase-specific input preparation
        if phase_number == 1:  # Forecast Unification
            base_input["forecast_models"] = ["prophet", "xgboost", "lightgbm"]
            base_input["confidence_threshold"] = settings.ml_confidence_threshold
        elif phase_number == 2:  # BOM Explosion
            base_input["bom_levels"] = 5
        elif phase_number == 3:  # Inventory Netting
            base_input["safety_stock_multiplier"] = 1.2
        elif phase_number == 4:  # Procurement Optimization
            base_input["algorithm"] = request.algorithm
            base_input["objective"] = request.objective
        elif phase_number == 5:  # Supplier Selection
            base_input["supplier_criteria"] = ["cost", "quality", "delivery", "reliability"]
        
        return base_input
    
    async def _generate_results(
        self,
        phase_results: Dict[str, Any],
        execution_time: float
    ) -> Dict[str, Any]:
        """Generate final planning results"""
        return {
            "planning_run_id": str(self.current_run.id),
            "status": "completed",
            "execution_time_seconds": execution_time,
            "phases_completed": len(phase_results),
            "total_cost": self._calculate_total_cost(phase_results),
            "total_units": self._calculate_total_units(phase_results),
            "optimization_score": self._calculate_optimization_score(phase_results),
            "recommendations": self._generate_recommendations(phase_results),
            "phase_results": phase_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_total_cost(self, phase_results: Dict[str, Any]) -> float:
        """Calculate total planning cost"""
        procurement = phase_results.get("ProcurementOptimization", {})
        return procurement.get("total_cost", 0.0)
    
    def _calculate_total_units(self, phase_results: Dict[str, Any]) -> int:
        """Calculate total units planned"""
        bom = phase_results.get("BOMExplosion", {})
        return bom.get("total_units", 0)
    
    def _calculate_optimization_score(self, phase_results: Dict[str, Any]) -> float:
        """Calculate optimization score (0-100)"""
        # Simplified scoring logic
        score = 85.0  # Base score
        
        # Adjust based on forecast confidence
        forecast = phase_results.get("ForecastUnification", {})
        if forecast.get("confidence", 0) > 0.8:
            score += 5
        
        # Adjust based on inventory utilization
        inventory = phase_results.get("InventoryNetting", {})
        if inventory.get("utilization_rate", 0) > 0.7:
            score += 5
        
        # Adjust based on cost optimization
        procurement = phase_results.get("ProcurementOptimization", {})
        if procurement.get("cost_reduction_percent", 0) > 10:
            score += 5
        
        return min(100.0, score)
    
    def _generate_recommendations(self, phase_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Forecast recommendations
        forecast = phase_results.get("ForecastUnification", {})
        if forecast.get("confidence", 1.0) < 0.7:
            recommendations.append("Consider gathering more historical data to improve forecast accuracy")
        
        # Inventory recommendations
        inventory = phase_results.get("InventoryNetting", {})
        if inventory.get("stockout_risk", []):
            recommendations.append(f"High stockout risk for {len(inventory['stockout_risk'])} items - consider expediting orders")
        
        # Supplier recommendations
        supplier = phase_results.get("SupplierSelection", {})
        if supplier.get("single_source_items", []):
            recommendations.append(f"Consider diversifying suppliers for {len(supplier['single_source_items'])} single-sourced items")
        
        return recommendations