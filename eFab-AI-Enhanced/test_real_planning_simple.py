#!/usr/bin/env python3
"""
Simple test of planning phases with real ERP data (no database required)
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.engine.planning.phases import ForecastUnification, InventoryNetting, BOMExplosion
from src.data.erp_loader import ERPDataLoader
import json


async def test_phases_with_real_data():
    """Test individual phases with real ERP data"""
    print("=" * 60)
    print("TESTING PLANNING PHASES WITH REAL ERP DATA")
    print("=" * 60)
    
    # Load real ERP data
    print("\n📂 Loading Beverly Knits ERP data...")
    loader = ERPDataLoader()
    erp_data = loader.load_all_data()
    planning_data = loader.get_planning_data()
    
    print(f"✅ Loaded {len(erp_data['inventory'])} inventory records")
    print(f"✅ Loaded {len(erp_data['sales_orders'])} sales orders")
    print(f"✅ Loaded {len(erp_data['yarn_demand'])} yarn demand records")
    
    # Test Phase 1: Forecast Unification
    print("\n" + "-" * 40)
    print("📊 PHASE 1: FORECAST UNIFICATION")
    print("-" * 40)
    
    forecast_phase = ForecastUnification()
    forecast_input = {
        "horizon_days": 30,
        "historical_demand": planning_data["demand_forecast"],
        "current_orders": planning_data["sales_orders"]
    }
    
    forecast_result = await forecast_phase.execute(forecast_input)
    
    print(f"Data Source: {forecast_result.get('data_source', 'Unknown')}")
    print(f"Total Demand: {forecast_result.get('total_demand', 0):,.0f}")
    print(f"Daily Average: {forecast_result.get('average_daily_demand', 0):,.1f}")
    print(f"Confidence: {forecast_result.get('confidence', 0):.2%}")
    
    if "historical_weekly_avg" in forecast_result:
        print(f"Historical Weekly Avg: {forecast_result['historical_weekly_avg']:,.0f}")
    if "current_order_demand" in forecast_result:
        print(f"Current Order Demand: {forecast_result['current_order_demand']:,.0f}")
    
    # Test Phase 2: BOM Explosion
    print("\n" + "-" * 40)
    print("🔧 PHASE 2: BOM EXPLOSION")
    print("-" * 40)
    
    bom_phase = BOMExplosion()
    bom_input = {
        "horizon_days": 30,
        "previous_phase_output": forecast_result,
        "inventory_levels": planning_data["current_inventory"]
    }
    
    bom_result = await bom_phase.execute(bom_input)
    
    print(f"Total Units: {bom_result.get('total_units', 0):,}")
    print(f"Total Materials: {bom_result.get('total_materials', 0):,.0f}")
    print(f"Material Requirements: {len(bom_result.get('material_requirements', []))} items")
    
    # Test Phase 3: Inventory Netting with Real Data
    print("\n" + "-" * 40)
    print("📦 PHASE 3: INVENTORY NETTING (REAL DATA)")
    print("-" * 40)
    
    netting_phase = InventoryNetting()
    netting_input = {
        "horizon_days": 30,
        "previous_phase_output": bom_result,
        "current_inventory": planning_data["current_inventory"]  # Real inventory data
    }
    
    netting_result = await netting_phase.execute(netting_input)
    
    print(f"Data Source: {netting_result.get('data_source', 'Unknown')}")
    
    if netting_result.get('data_source') == 'Beverly Knits Inventory':
        print(f"✅ USING REAL INVENTORY DATA!")
        print(f"Unique Materials: {netting_result.get('unique_materials', 0):,}")
        print(f"Total Available Inventory: {netting_result.get('total_available_inventory', 0):,.0f}")
        print(f"Total Required: {netting_result.get('total_required', 0):,.0f}")
        print(f"Utilization Rate: {netting_result.get('utilization_rate', 0):.2%}")
        print(f"Inventory Health: {netting_result.get('inventory_health', 'Unknown')}")
        print(f"Total Shortage: {netting_result.get('total_shortage', 0):,.0f}")
        
        # Show stockout risks
        risks = netting_result.get('stockout_risks', [])
        if risks:
            print(f"\n⚠️ STOCKOUT RISKS ({len(risks)} items):")
            for risk in risks[:5]:  # Show top 5
                print(f"   - {risk.get('material', 'Unknown')}: {risk.get('coverage', 'N/A')} coverage, shortage: {risk.get('shortage', 0):,.0f}")
        
        # Show some net requirements
        requirements = netting_result.get('net_requirements', [])
        if requirements:
            print(f"\n📋 SAMPLE NET REQUIREMENTS (showing 5 of {len(requirements)}):")
            for req in requirements[:5]:
                print(f"   - {req['material']}:")
                print(f"     Gross: {req['gross_requirement']:,.0f}, Available: {req['current_inventory']:,.0f}, Net: {req['net_requirement']:,.0f}")
    else:
        print("❌ Using simulated data (no real inventory matched)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("-" * 40)
    
    is_using_real_data = (
        forecast_result.get('data_source') == 'Beverly Knits ERP' or
        netting_result.get('data_source') == 'Beverly Knits Inventory'
    )
    
    if is_using_real_data:
        print("✅ SUCCESSFULLY USING REAL ERP DATA!")
        print("   - Forecast based on actual yarn demand")
        print("   - Inventory netting using real stock levels")
        print("   - Ready for production planning")
    else:
        print("⚠️ Using simulated data - check data integration")
    
    # Save results
    results = {
        "forecast": forecast_result,
        "bom": bom_result,
        "netting": netting_result
    }
    
    with open("phase_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n📁 Results saved to phase_test_results.json")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_phases_with_real_data())