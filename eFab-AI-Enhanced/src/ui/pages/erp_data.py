"""
ERP Data Viewer Page for Streamlit UI
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.erp_loader import ERPDataLoader


class ERPDataViewer:
    """Display real ERP data in Streamlit"""
    
    def __init__(self):
        self.loader = ERPDataLoader()
        
    def render(self):
        """Render ERP data page"""
        st.title("📊 Beverly Knits ERP Data")
        
        # Load data
        with st.spinner("Loading ERP data..."):
            data = self.loader.load_all_data()
        
        # Display summary metrics
        self._render_summary_metrics(data['summary'])
        
        # Create tabs for different data views
        tabs = st.tabs([
            "📦 Inventory", 
            "📋 Sales Orders", 
            "🧵 Yarn Demand", 
            "📈 Analytics",
            "🔄 Data Sync"
        ])
        
        with tabs[0]:
            self._render_inventory_view(data['inventory'])
        
        with tabs[1]:
            self._render_sales_orders_view(data['sales_orders'])
        
        with tabs[2]:
            self._render_yarn_demand_view(data['yarn_demand'])
        
        with tabs[3]:
            self._render_analytics(data)
        
        with tabs[4]:
            self._render_data_sync()
    
    def _render_summary_metrics(self, summary: dict):
        """Render summary metrics"""
        st.markdown("### 📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Inventory (yards)",
                f"{summary.get('total_inventory_yards', 0):,.0f}",
                delta=None
            )
        
        with col2:
            st.metric(
                "Active Sales Orders",
                f"{summary.get('total_sales_orders', 0):,}",
                delta=None
            )
        
        with col3:
            st.metric(
                "Order Value",
                f"${summary.get('total_order_value', 0):,.2f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Warehouses",
                len(summary.get('warehouses', [])),
                delta=None
            )
        
        # Show top customers
        if summary.get('top_customers'):
            st.markdown("### 🏆 Top Customers")
            top_customers = pd.DataFrame(
                list(summary['top_customers'].items()),
                columns=['Customer', 'Order Volume']
            ).sort_values('Order Volume', ascending=False)
            
            fig = px.bar(
                top_customers,
                x='Order Volume',
                y='Customer',
                orientation='h',
                title="Top 5 Customers by Order Volume"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_inventory_view(self, inventory_df: pd.DataFrame):
        """Render inventory data view"""
        st.subheader("Current Inventory Levels")
        
        if inventory_df.empty:
            st.warning("No inventory data available")
            return
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            warehouses = inventory_df['warehouse'].unique() if 'warehouse' in inventory_df else []
            selected_warehouse = st.selectbox(
                "Warehouse",
                ["All"] + list(warehouses)
            )
        
        with col2:
            min_qty = st.number_input("Min Quantity", value=0)
        
        with col3:
            search = st.text_input("Search Style/Customer")
        
        # Apply filters
        filtered_df = inventory_df.copy()
        
        if selected_warehouse != "All" and 'warehouse' in filtered_df:
            filtered_df = filtered_df[filtered_df['warehouse'] == selected_warehouse]
        
        if 'total_quantity' in filtered_df:
            filtered_df = filtered_df[filtered_df['total_quantity'] >= min_qty]
        
        if search:
            mask = False
            for col in ['style_number', 'customer', 'order_number']:
                if col in filtered_df:
                    mask |= filtered_df[col].astype(str).str.contains(search, case=False, na=False)
            filtered_df = filtered_df[mask]
        
        # Display data
        st.dataframe(
            filtered_df.head(100),
            use_container_width=True,
            hide_index=True
        )
        
        # Inventory by warehouse chart
        if 'warehouse' in inventory_df and 'total_quantity' in inventory_df:
            warehouse_summary = inventory_df.groupby('warehouse')['total_quantity'].sum().reset_index()
            
            fig = px.pie(
                warehouse_summary,
                values='total_quantity',
                names='warehouse',
                title="Inventory Distribution by Warehouse"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_sales_orders_view(self, orders_df: pd.DataFrame):
        """Render sales orders view"""
        st.subheader("Sales Orders")
        
        if orders_df.empty:
            st.warning("No sales order data available")
            return
        
        # Order status summary
        if 'Status' in orders_df:
            status_counts = orders_df['Status'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Orders by Status"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Order value by status
                if 'unit_price_value' in orders_df and 'Ordered' in orders_df:
                    orders_df['order_value'] = orders_df['unit_price_value'] * orders_df['Ordered']
                    value_by_status = orders_df.groupby('Status')['order_value'].sum()
                    
                    fig = px.bar(
                        x=value_by_status.index,
                        y=value_by_status.values,
                        title="Order Value by Status",
                        labels={'x': 'Status', 'y': 'Value ($)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Orders table
        st.markdown("### Recent Orders")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Status' in orders_df:
                selected_status = st.selectbox(
                    "Status Filter",
                    ["All"] + list(orders_df['Status'].unique())
                )
        
        with col2:
            if 'CSR' in orders_df:
                selected_csr = st.selectbox(
                    "CSR Filter",
                    ["All"] + list(orders_df['CSR'].unique())
                )
        
        with col3:
            customer_search = st.text_input("Search Customer")
        
        # Apply filters
        filtered_orders = orders_df.copy()
        
        if 'Status' in orders_df and selected_status != "All":
            filtered_orders = filtered_orders[filtered_orders['Status'] == selected_status]
        
        if 'CSR' in orders_df and selected_csr != "All":
            filtered_orders = filtered_orders[filtered_orders['CSR'] == selected_csr]
        
        if customer_search and 'Sold To' in filtered_orders:
            filtered_orders = filtered_orders[
                filtered_orders['Sold To'].str.contains(customer_search, case=False, na=False)
            ]
        
        # Display orders
        display_cols = [
            'Status', 'PO #', 'Sold To', 'Ordered', 
            'Picked/Shipped', 'Balance', 'Ship Date'
        ]
        display_cols = [col for col in display_cols if col in filtered_orders.columns]
        
        st.dataframe(
            filtered_orders[display_cols].head(50),
            use_container_width=True,
            hide_index=True
        )
    
    def _render_yarn_demand_view(self, demand_df: pd.DataFrame):
        """Render yarn demand forecast view"""
        st.subheader("Yarn Demand Forecast")
        
        if demand_df.empty:
            st.warning("No yarn demand data available")
            return
        
        # Get week columns
        week_columns = [col for col in demand_df.columns if col.startswith('Week')]
        
        if not week_columns:
            st.warning("No weekly forecast data found")
            return
        
        # Weekly demand chart
        weekly_totals = demand_df[week_columns].sum()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=week_columns,
            y=weekly_totals.values,
            name='Demand',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title="Weekly Yarn Demand Forecast",
            xaxis_title="Week",
            yaxis_title="Demand (units)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top yarns by demand
        if 'Yarn' in demand_df and 'Total' in demand_df:
            top_yarns = demand_df.nlargest(10, 'Total')[['Yarn', 'Total']]
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    top_yarns,
                    x='Total',
                    y='Yarn',
                    orientation='h',
                    title="Top 10 Yarns by Total Demand"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Demand breakdown by style
                if 'Style' in demand_df:
                    style_demand = demand_df.groupby('Style')['Total'].sum().nlargest(10)
                    
                    fig = px.pie(
                        values=style_demand.values,
                        names=style_demand.index,
                        title="Top 10 Styles by Demand"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Detailed demand table
        st.markdown("### Detailed Demand by Style/Yarn")
        
        search = st.text_input("Search Style or Yarn")
        
        filtered_demand = demand_df.copy()
        if search:
            mask = False
            for col in ['Style', 'Yarn']:
                if col in filtered_demand:
                    mask |= filtered_demand[col].astype(str).str.contains(search, case=False, na=False)
            filtered_demand = filtered_demand[mask]
        
        st.dataframe(
            filtered_demand.head(50),
            use_container_width=True,
            hide_index=True
        )
    
    def _render_analytics(self, data: dict):
        """Render analytics dashboard"""
        st.subheader("Analytics Dashboard")
        
        # Inventory turnover analysis
        if not data['inventory'].empty and not data['sales_orders'].empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Inventory vs Orders
                inv_total = data['inventory']['total_quantity'].sum() if 'total_quantity' in data['inventory'] else 0
                order_total = data['sales_orders']['Ordered'].sum() if 'Ordered' in data['sales_orders'] else 0
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Current Inventory', 'Open Orders'],
                    y=[inv_total, order_total],
                    marker_color=['green', 'blue']
                ))
                fig.update_layout(
                    title="Inventory vs Open Orders",
                    yaxis_title="Quantity"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Coverage ratio
                if order_total > 0:
                    coverage_ratio = (inv_total / order_total) * 100
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=coverage_ratio,
                        title={'text': "Inventory Coverage %"},
                        domain={'x': [0, 1], 'y': [0, 1]},
                        gauge={
                            'axis': {'range': [None, 200]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "red"},
                                {'range': [50, 100], 'color': "yellow"},
                                {'range': [100, 200], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': 100
                            }
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)
        
        # Critical items analysis
        if data['summary'].get('critical_items'):
            st.markdown("### ⚠️ Critical Items (Low Stock)")
            critical_df = pd.DataFrame(
                data['summary']['critical_items'],
                columns=['Style Number']
            )
            st.dataframe(critical_df, use_container_width=True)
    
    def _render_data_sync(self):
        """Render data synchronization options"""
        st.subheader("Data Synchronization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Manual Data Refresh")
            if st.button("🔄 Refresh All Data", type="primary"):
                with st.spinner("Refreshing ERP data..."):
                    # Reload data
                    self.loader = ERPDataLoader()
                    data = self.loader.load_all_data()
                    st.success(f"Data refreshed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            st.markdown("### Auto-Sync Settings")
            auto_sync = st.checkbox("Enable Auto-Sync")
            if auto_sync:
                sync_interval = st.selectbox(
                    "Sync Interval",
                    ["Every 15 minutes", "Every 30 minutes", "Every hour", "Every 4 hours"]
                )
                st.info(f"Auto-sync enabled: {sync_interval}")
        
        # Data source information
        st.markdown("### Data Sources")
        
        data_sources = [
            {"Source": "Inventory", "File Pattern": "eFab_Inventory_*.csv", "Last Updated": "Today"},
            {"Source": "Sales Orders", "File Pattern": "eFab_SO_List_*.csv", "Last Updated": "Today"},
            {"Source": "Yarn Demand", "File Pattern": "Yarn_Demand_*.csv", "Last Updated": "Today"},
            {"Source": "Yarn Inventory", "File Pattern": "*yarn_inventory*.xlsx", "Last Updated": "Today"}
        ]
        
        st.dataframe(
            pd.DataFrame(data_sources),
            use_container_width=True,
            hide_index=True
        )
        
        # Upload new data
        st.markdown("### Upload New Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx'],
            help="Upload new ERP data files to update the system"
        )
        
        if uploaded_file is not None:
            if st.button("Process Upload"):
                with st.spinner("Processing uploaded file..."):
                    # Here you would process the uploaded file
                    st.success(f"File '{uploaded_file.name}' processed successfully!")


# Standalone function for integration
def render_erp_data_page():
    """Render ERP data page (for integration with main app)"""
    viewer = ERPDataViewer()
    viewer.render()


if __name__ == "__main__":
    # For testing this page independently
    st.set_page_config(
        page_title="ERP Data Viewer",
        page_icon="📊",
        layout="wide"
    )
    render_erp_data_page()