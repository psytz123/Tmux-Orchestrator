#!/usr/bin/env python3
"""
Test the planning engine with real ERP data
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.engine.planning.real_data_engine import RealDataPlanningEngine
from src.engine.planning.engine import PlanningRequest
import json


async def test_real_data_planning():
    """Test planning with real ERP data"""
    print("=" * 60)
    print("TESTING PLANNING ENGINE WITH REAL ERP DATA")
    print("=" * 60)
    
    # Create planning engine
    engine = RealDataPlanningEngine()
    
    # Create planning request
    request = PlanningRequest(
        name="Test Plan with Real Data",
        horizon_days=30,
        algorithm="mixed_integer",
        objective="minimize_cost",
        parameters={
            "use_real_data": True,
            "confidence_threshold": 0.7
        }
    )
    
    print("\n📊 Starting planning run with real Beverly Knits data...")
    print(f"   Horizon: {request.horizon_days} days")
    print(f"   Algorithm: {request.algorithm}")
    print(f"   Objective: {request.objective}")
    
    try:
        # Execute planning
        results = await engine.execute_planning(request)
        
        print("\n✅ PLANNING COMPLETED SUCCESSFULLY!")
        print("-" * 40)
        
        # Display phase results
        if "phase_results" in results:
            for phase_name, phase_data in results["phase_results"].items():
                print(f"\n📌 {phase_name}:")
                
                # Check data source
                if "data_source" in phase_data:
                    print(f"   Data Source: {phase_data['data_source']}")
                
                # Phase-specific outputs
                if phase_name == "ForecastUnification":
                    print(f"   Total Demand: {phase_data.get('total_demand', 0):.0f}")
                    print(f"   Daily Average: {phase_data.get('average_daily_demand', 0):.1f}")
                    print(f"   Confidence: {phase_data.get('confidence', 0):.2%}")
                    if "historical_weekly_avg" in phase_data:
                        print(f"   Historical Weekly Avg: {phase_data['historical_weekly_avg']:.0f}")
                    if "current_order_demand" in phase_data:
                        print(f"   Current Order Demand: {phase_data['current_order_demand']:.0f}")
                
                elif phase_name == "InventoryNetting":
                    print(f"   Unique Materials: {phase_data.get('unique_materials', 0)}")
                    print(f"   Total Available: {phase_data.get('total_available_inventory', 0):.0f}")
                    print(f"   Total Required: {phase_data.get('total_required', 0):.0f}")
                    print(f"   Utilization Rate: {phase_data.get('utilization_rate', 0):.2%}")
                    print(f"   Inventory Health: {phase_data.get('inventory_health', 'Unknown')}")
                    
                    # Show stockout risks if any
                    risks = phase_data.get('stockout_risks', [])
                    if risks:
                        print(f"   ⚠️ Stockout Risks: {len(risks)} items")
                        for risk in risks[:3]:  # Show top 3
                            print(f"      - {risk.get('material', 'Unknown')}: {risk.get('coverage', 'N/A')} coverage")
        
        # Overall results
        print("\n📈 OVERALL RESULTS:")
        print("-" * 40)
        print(f"Total Cost: ${results.get('total_cost', 0):,.2f}")
        print(f"Optimization Score: {results.get('optimization_score', 0):.1f}/100")
        print(f"Execution Time: {results.get('execution_time_seconds', 0):.2f} seconds")
        
        # Recommendations
        if "recommendations" in results:
            print("\n💡 RECOMMENDATIONS:")
            for rec in results["recommendations"]:
                print(f"   • {rec}")
        
        # Save results
        with open("planning_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print("\n📁 Full results saved to planning_results.json")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_real_data_planning())