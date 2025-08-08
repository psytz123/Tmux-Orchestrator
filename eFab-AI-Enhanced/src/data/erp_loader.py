"""
ERP Data Loader for real Beverly Knits data
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class ERPDataLoader:
    """Load and process ERP data from CSV/Excel files"""
    
    def __init__(self, data_path: str = "/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/ERP Data"):
        self.data_path = Path(data_path)
        self.inventory_data = {}
        self.sales_orders = pd.DataFrame()
        self.yarn_demand = pd.DataFrame()
        self.yarn_inventory = pd.DataFrame()
        
    def load_all_data(self) -> Dict[str, Any]:
        """Load all available ERP data"""
        logger.info("Loading ERP data from Beverly Knits system...")
        
        data = {
            "inventory": self.load_inventory(),
            "sales_orders": self.load_sales_orders(),
            "yarn_demand": self.load_yarn_demand(),
            "yarn_inventory": self.load_yarn_inventory(),
            "summary": self.generate_summary()
        }
        
        logger.info(f"Loaded {len(data['inventory'])} inventory records")
        logger.info(f"Loaded {len(data['sales_orders'])} sales orders")
        logger.info(f"Loaded {len(data['yarn_demand'])} yarn demand records")
        
        return data
    
    def load_inventory(self) -> pd.DataFrame:
        """Load inventory data from multiple warehouse files"""
        inventory_files = list(self.data_path.glob("eFab_Inventory_*.csv"))
        
        all_inventory = []
        
        for file in inventory_files:
            try:
                # Extract warehouse code from filename
                warehouse = file.stem.split('_')[2][:3]  # e.g., F01, G00, I01
                
                # Read CSV with specific handling for Beverly Knits format
                df = pd.read_csv(file, encoding='utf-8-sig')
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Add warehouse identifier
                df['warehouse'] = warehouse
                
                # Parse and clean data
                if 'Qty (yds)' in df.columns:
                    df['quantity_yards'] = pd.to_numeric(
                        df['Qty (yds)'].astype(str).str.replace(',', ''), 
                        errors='coerce'
                    )
                    
                if 'Qty (lbs)' in df.columns:
                    df['quantity_lbs'] = pd.to_numeric(
                        df['Qty (lbs)'].astype(str).str.replace(',', ''), 
                        errors='coerce'
                    )
                
                all_inventory.append(df)
                
            except Exception as e:
                logger.warning(f"Error loading {file}: {e}")
                continue
        
        if all_inventory:
            self.inventory_data = pd.concat(all_inventory, ignore_index=True)
            
            # Clean and standardize
            self.inventory_data = self._clean_inventory_data(self.inventory_data)
            
            return self.inventory_data
        
        return pd.DataFrame()
    
    def load_sales_orders(self) -> pd.DataFrame:
        """Load sales order data"""
        so_files = list(self.data_path.glob("eFab_SO_List_*.csv"))
        
        if not so_files:
            logger.warning("No sales order files found")
            return pd.DataFrame()
        
        # Use most recent file
        latest_so = max(so_files, key=lambda f: f.stat().st_mtime)
        
        try:
            df = pd.read_csv(latest_so, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            
            # Parse numeric fields
            numeric_fields = ['Ordered', 'Picked/Shipped', 'Balance', 'Available']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(
                        df[field].astype(str).str.replace(',', ''), 
                        errors='coerce'
                    )
            
            # Parse unit price
            if 'Unit Price' in df.columns:
                df['unit_price_value'] = df['Unit Price'].str.extract(r'\$(\d+\.?\d*)')[0].astype(float)
                df['unit_price_uom'] = df['Unit Price'].str.extract(r'\((.*?)\)')[0]
            
            # Parse dates
            date_fields = ['Quoted Date', 'Ship Date']
            for field in date_fields:
                if field in df.columns:
                    df[field] = pd.to_datetime(df[field], errors='coerce')
            
            self.sales_orders = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading sales orders: {e}")
            return pd.DataFrame()
    
    def load_yarn_demand(self) -> pd.DataFrame:
        """Load yarn demand forecast data"""
        demand_files = list(self.data_path.glob("Yarn_Demand_*.csv"))
        
        if not demand_files:
            logger.warning("No yarn demand files found")
            return pd.DataFrame()
        
        # Use most recent file
        latest_demand = max(demand_files, key=lambda f: f.stat().st_mtime)
        
        try:
            df = pd.read_csv(latest_demand, encoding='utf-8-sig')
            df.columns = df.columns.str.strip()
            
            # Parse numeric columns (week columns and totals)
            week_columns = [col for col in df.columns if col.startswith('Week') or col in ['This Week', 'Later', 'Total']]
            
            for col in week_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(
                        df[col].astype(str).str.replace(',', ''), 
                        errors='coerce'
                    )
            
            self.yarn_demand = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading yarn demand: {e}")
            return pd.DataFrame()
    
    def load_yarn_inventory(self) -> pd.DataFrame:
        """Load yarn inventory data"""
        yarn_files = list(self.data_path.glob("*yarn_inventory*.xlsx"))
        
        if not yarn_files:
            # Try CSV files
            yarn_files = list(self.data_path.glob("*yarn_inventory*.csv"))
        
        if not yarn_files:
            logger.warning("No yarn inventory files found")
            return pd.DataFrame()
        
        latest_yarn = max(yarn_files, key=lambda f: f.stat().st_mtime)
        
        try:
            if latest_yarn.suffix == '.xlsx':
                df = pd.read_excel(latest_yarn)
            else:
                df = pd.read_csv(latest_yarn, encoding='utf-8-sig')
            
            df.columns = df.columns.str.strip()
            self.yarn_inventory = df
            return df
            
        except Exception as e:
            logger.error(f"Error loading yarn inventory: {e}")
            return pd.DataFrame()
    
    def _clean_inventory_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize inventory data"""
        # Remove HTML artifacts if present
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(r'<[^>]+>', '', regex=True)
                df[col] = df[col].str.strip()
        
        # Standardize column names
        column_mapping = {
            'Style #': 'style_number',
            'Order #': 'order_number',
            'Customer': 'customer',
            'Roll #': 'roll_number',
            'Vendor Roll #': 'vendor_roll',
            'Rack': 'rack_location',
            'Good Ea.': 'good_units',
            'Bad Ea.': 'bad_units',
            'Received': 'date_received'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Parse date received
        if 'date_received' in df.columns:
            df['date_received'] = pd.to_datetime(df['date_received'], errors='coerce')
        
        # Calculate total quantity in standard units (yards)
        if 'quantity_yards' in df.columns:
            df['total_quantity'] = df['quantity_yards'].fillna(0)
        elif 'quantity_lbs' in df.columns:
            # Convert lbs to yards (approximate conversion for fabric)
            df['total_quantity'] = df['quantity_lbs'].fillna(0) * 3.5  # Rough conversion factor
        
        return df
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics from loaded data"""
        summary = {
            "total_inventory_value": 0,
            "total_sales_orders": len(self.sales_orders),
            "total_yarn_types": 0,
            "warehouses": [],
            "top_customers": [],
            "critical_items": [],
            "demand_forecast": {}
        }
        
        # Inventory summary
        if not self.inventory_data.empty:
            summary["total_inventory_yards"] = self.inventory_data.get('quantity_yards', pd.Series()).sum()
            summary["total_inventory_lbs"] = self.inventory_data.get('quantity_lbs', pd.Series()).sum()
            summary["warehouses"] = self.inventory_data['warehouse'].unique().tolist() if 'warehouse' in self.inventory_data else []
        
        # Sales order summary
        if not self.sales_orders.empty:
            summary["total_order_value"] = (
                self.sales_orders['Ordered'] * self.sales_orders.get('unit_price_value', 0)
            ).sum() if 'Ordered' in self.sales_orders else 0
            
            if 'Sold To' in self.sales_orders:
                top_customers = self.sales_orders.groupby('Sold To')['Ordered'].sum().nlargest(5)
                summary["top_customers"] = top_customers.to_dict()
        
        # Yarn demand summary
        if not self.yarn_demand.empty:
            week_cols = [col for col in self.yarn_demand.columns if col.startswith('Week')]
            if week_cols:
                summary["demand_forecast"] = {
                    "weeks": week_cols,
                    "total_demand": self.yarn_demand[week_cols].sum().to_dict()
                }
        
        # Identify critical items (low stock vs demand)
        if not self.inventory_data.empty and not self.yarn_demand.empty:
            # This would require matching inventory to demand - simplified for now
            low_stock = self.inventory_data[
                self.inventory_data.get('total_quantity', pd.Series()) < 100
            ]
            if not low_stock.empty and 'style_number' in low_stock:
                summary["critical_items"] = low_stock['style_number'].head(10).tolist()
        
        return summary
    
    def get_planning_data(self) -> Dict[str, Any]:
        """Get data formatted for planning engine"""
        return {
            "current_inventory": self._format_inventory_for_planning(),
            "demand_forecast": self._format_demand_for_planning(),
            "sales_orders": self._format_orders_for_planning(),
            "supplier_info": self._extract_supplier_info(),
            "lead_times": self._calculate_lead_times()
        }
    
    def _format_inventory_for_planning(self) -> List[Dict]:
        """Format inventory data for planning engine"""
        if self.inventory_data.empty:
            return []
        
        inventory = []
        for _, row in self.inventory_data.iterrows():
            inventory.append({
                "material_id": row.get('style_number', 'Unknown'),
                "warehouse": row.get('warehouse', 'Main'),
                "current_stock": float(row.get('total_quantity', 0)),
                "unit_of_measure": "yards",
                "location": row.get('rack_location', 'Unknown')
            })
        
        return inventory
    
    def _format_demand_for_planning(self) -> Dict[str, List]:
        """Format demand forecast for planning engine"""
        if self.yarn_demand.empty:
            return {}
        
        demand = {}
        week_cols = [col for col in self.yarn_demand.columns if col.startswith('Week')]
        
        for _, row in self.yarn_demand.iterrows():
            style = row.get('Style', 'Unknown')
            weekly_demand = []
            
            for week in week_cols:
                weekly_demand.append({
                    "week": week,
                    "quantity": float(row.get(week, 0))
                })
            
            demand[style] = weekly_demand
        
        return demand
    
    def _format_orders_for_planning(self) -> List[Dict]:
        """Format sales orders for planning engine"""
        if self.sales_orders.empty:
            return []
        
        orders = []
        for _, row in self.sales_orders.iterrows():
            orders.append({
                "order_id": row.get('PO #', 'Unknown'),
                "customer": row.get('Sold To', 'Unknown'),
                "status": row.get('Status', 'Unknown'),
                "quantity_ordered": float(row.get('Ordered', 0)),
                "quantity_shipped": float(row.get('Picked/Shipped', 0)),
                "balance": float(row.get('Balance', 0)),
                "ship_date": row.get('Ship Date', '').isoformat() if pd.notna(row.get('Ship Date')) else None,
                "unit_price": float(row.get('unit_price_value', 0))
            })
        
        return orders
    
    def _extract_supplier_info(self) -> List[Dict]:
        """Extract supplier information from data"""
        suppliers = []
        
        # Extract from vendor roll numbers in inventory
        if not self.inventory_data.empty and 'vendor_roll' in self.inventory_data:
            unique_vendors = self.inventory_data['vendor_roll'].dropna().unique()
            
            for vendor in unique_vendors[:10]:  # Limit to top 10
                suppliers.append({
                    "supplier_id": vendor,
                    "name": f"Vendor {vendor}",
                    "reliability_score": np.random.uniform(0.7, 0.95),  # Simulated
                    "lead_time_days": np.random.randint(7, 21)  # Simulated
                })
        
        return suppliers
    
    def _calculate_lead_times(self) -> Dict[str, int]:
        """Calculate average lead times from historical data"""
        lead_times = {}
        
        # Calculate from received dates if available
        if not self.inventory_data.empty and 'date_received' in self.inventory_data:
            # Group by style and calculate average days
            # This is simplified - real calculation would use order date
            lead_times["average_days"] = 14  # Default
            lead_times["min_days"] = 7
            lead_times["max_days"] = 30
        
        return lead_times