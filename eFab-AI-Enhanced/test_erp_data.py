#!/usr/bin/env python3
"""
Test script to verify ERP data integration
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.data.erp_loader import ERPDataLoader
import pandas as pd
import json


def test_erp_loader():
    """Test ERP data loading"""
    print("=" * 60)
    print("TESTING ERP DATA LOADER")
    print("=" * 60)
    
    # Initialize loader
    loader = ERPDataLoader()
    
    # Load all data
    print("\n📂 Loading ERP data...")
    data = loader.load_all_data()
    
    # Display summary
    print("\n📊 DATA SUMMARY:")
    print("-" * 40)
    
    # Inventory
    inventory = data['inventory']
    if not inventory.empty:
        print(f"✅ Inventory Records: {len(inventory)}")
        print(f"   Warehouses: {inventory['warehouse'].unique().tolist() if 'warehouse' in inventory else 'N/A'}")
        print(f"   Total Quantity (yards): {inventory['quantity_yards'].sum() if 'quantity_yards' in inventory else 0:,.0f}")
    else:
        print("❌ No inventory data loaded")
    
    # Sales Orders
    orders = data['sales_orders']
    if not orders.empty:
        print(f"\n✅ Sales Orders: {len(orders)}")
        if 'Status' in orders:
            print(f"   Order Status:")
            for status, count in orders['Status'].value_counts().items():
                print(f"      - {status}: {count}")
        if 'unit_price_value' in orders and 'Ordered' in orders:
            total_value = (orders['unit_price_value'] * orders['Ordered']).sum()
            print(f"   Total Order Value: ${total_value:,.2f}")
    else:
        print("\n❌ No sales order data loaded")
    
    # Yarn Demand
    demand = data['yarn_demand']
    if not demand.empty:
        print(f"\n✅ Yarn Demand Records: {len(demand)}")
        week_cols = [col for col in demand.columns if col.startswith('Week')]
        if week_cols:
            print(f"   Forecast Weeks: {len(week_cols)}")
            total_demand = demand[week_cols].sum().sum()
            print(f"   Total Forecasted Demand: {total_demand:,.0f}")
    else:
        print("\n❌ No yarn demand data loaded")
    
    # Summary
    summary = data['summary']
    print("\n📈 SUMMARY METRICS:")
    print("-" * 40)
    print(json.dumps(summary, indent=2, default=str))
    
    # Test planning data format
    print("\n🔧 TESTING PLANNING DATA FORMAT:")
    print("-" * 40)
    planning_data = loader.get_planning_data()
    
    print(f"✅ Current Inventory Items: {len(planning_data['current_inventory'])}")
    print(f"✅ Demand Forecast Styles: {len(planning_data['demand_forecast'])}")
    print(f"✅ Sales Orders: {len(planning_data['sales_orders'])}")
    print(f"✅ Suppliers: {len(planning_data['supplier_info'])}")
    print(f"✅ Lead Times: {planning_data['lead_times']}")
    
    # Sample data
    if planning_data['current_inventory']:
        print("\n📦 Sample Inventory Item:")
        print(json.dumps(planning_data['current_inventory'][0], indent=2, default=str))
    
    if planning_data['sales_orders']:
        print("\n📋 Sample Sales Order:")
        print(json.dumps(planning_data['sales_orders'][0], indent=2, default=str))
    
    print("\n" + "=" * 60)
    print("✅ ERP DATA INTEGRATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_erp_loader()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()