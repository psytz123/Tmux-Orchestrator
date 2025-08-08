"""
Streamlit UI for eFab AI Enhanced
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import ERP data viewer
try:
    from src.ui.pages.erp_data import ERPDataViewer
except ImportError:
    ERPDataViewer = None

# Page configuration
st.set_page_config(
    page_title="eFab AI Enhanced",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .status-running { background-color: #FEF3C7; color: #92400E; }
    .status-completed { background-color: #D1FAE5; color: #065F46; }
    .status-failed { background-color: #FEE2E2; color: #991B1B; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'planning_runs' not in st.session_state:
    st.session_state.planning_runs = []
if 'current_run' not in st.session_state:
    st.session_state.current_run = None


class eFabUI:
    """Main UI Application"""
    
    def __init__(self):
        self.api_base = "http://localhost:8000/api/v1"
        
    def run(self):
        """Run the main application"""
        # Sidebar navigation
        with st.sidebar:
            st.image("https://via.placeholder.com/300x100?text=eFab+AI", use_column_width=True)
            st.markdown("---")
            
            page = st.selectbox(
                "Navigation",
                ["🏠 Dashboard", "📊 Planning", "📦 Inventory", "📈 Forecasting", "📉 Analytics", "🗄️ ERP Data", "⚙️ Settings"]
            )
            
            st.markdown("---")
            self._render_system_status()
        
        # Main content
        if page == "🏠 Dashboard":
            self.render_dashboard()
        elif page == "📊 Planning":
            self.render_planning()
        elif page == "📦 Inventory":
            self.render_inventory()
        elif page == "📈 Forecasting":
            self.render_forecasting()
        elif page == "📉 Analytics":
            self.render_analytics()
        elif page == "🗄️ ERP Data":
            self.render_erp_data()
        elif page == "⚙️ Settings":
            self.render_settings()
    
    def render_dashboard(self):
        """Render main dashboard"""
        st.markdown('<h1 class="main-header">eFab AI Enhanced Dashboard</h1>', unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Active Planning Runs",
                value="3",
                delta="+1 from yesterday"
            )
        
        with col2:
            st.metric(
                label="Inventory Health",
                value="87%",
                delta="+5%"
            )
        
        with col3:
            st.metric(
                label="Forecast Accuracy",
                value="92.3%",
                delta="+2.1%"
            )
        
        with col4:
            st.metric(
                label="Cost Savings",
                value="$45.2K",
                delta="+$5.1K"
            )
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Demand Forecast")
            self._render_demand_forecast_chart()
        
        with col2:
            st.subheader("📊 Inventory Levels")
            self._render_inventory_chart()
        
        # Recent activities
        st.markdown("---")
        st.subheader("🔄 Recent Activities")
        self._render_recent_activities()
    
    def render_planning(self):
        """Render planning page"""
        st.title("📊 Supply Chain Planning")
        
        tabs = st.tabs(["Create New Plan", "Active Plans", "History", "6-Phase Monitor"])
        
        with tabs[0]:
            self._render_create_plan()
        
        with tabs[1]:
            self._render_active_plans()
        
        with tabs[2]:
            self._render_planning_history()
        
        with tabs[3]:
            self._render_phase_monitor()
    
    def render_inventory(self):
        """Render inventory page"""
        st.title("📦 Inventory Management")
        
        # Inventory overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total SKUs", "1,247")
        with col2:
            st.metric("Low Stock Items", "23", delta_color="inverse")
        with col3:
            st.metric("Overstock Items", "45")
        
        st.markdown("---")
        
        # Inventory table
        st.subheader("Current Inventory Levels")
        self._render_inventory_table()
    
    def render_forecasting(self):
        """Render forecasting page"""
        st.title("📈 Demand Forecasting")
        
        # Model selection
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Model Configuration")
            models = st.multiselect(
                "Select Models",
                ["Prophet", "XGBoost", "LightGBM", "LSTM", "ARIMA"],
                default=["Prophet", "XGBoost", "LightGBM"]
            )
            
            horizon = st.slider("Forecast Horizon (days)", 7, 90, 30)
            
            confidence = st.slider("Confidence Threshold", 0.5, 1.0, 0.8, 0.05)
            
            if st.button("Generate Forecast", type="primary"):
                with st.spinner("Generating forecast..."):
                    # Simulate forecast generation
                    import time
                    time.sleep(2)
                    st.success("Forecast generated successfully!")
        
        with col2:
            st.subheader("Forecast Results")
            self._render_forecast_results()
    
    def render_erp_data(self):
        """Render ERP data page"""
        if ERPDataViewer:
            viewer = ERPDataViewer()
            viewer.render()
        else:
            st.error("ERP Data Viewer not available. Please check installation.")
    
    def render_analytics(self):
        """Render analytics page"""
        st.title("📉 Analytics & Insights")
        
        # Analytics dashboard
        metrics = st.columns(4)
        with metrics[0]:
            st.metric("Avg Lead Time", "12.3 days", "-1.2 days")
        with metrics[1]:
            st.metric("Order Fill Rate", "94.5%", "+2.3%")
        with metrics[2]:
            st.metric("Supplier Performance", "88%", "+5%")
        with metrics[3]:
            st.metric("Planning Efficiency", "91%", "+3%")
        
        st.markdown("---")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Supply Chain Performance")
            self._render_performance_chart()
        
        with col2:
            st.subheader("Cost Analysis")
            self._render_cost_analysis()
    
    def render_settings(self):
        """Render settings page"""
        st.title("⚙️ System Settings")
        
        tabs = st.tabs(["General", "Planning Engine", "ML Models", "Integrations"])
        
        with tabs[0]:
            st.subheader("General Settings")
            st.text_input("Company Name", value="eFab Textiles")
            st.selectbox("Time Zone", ["UTC", "EST", "PST", "CST"])
            st.selectbox("Language", ["English", "Spanish", "Chinese"])
        
        with tabs[1]:
            st.subheader("Planning Engine Configuration")
            st.selectbox("Optimization Algorithm", ["Mixed Integer", "Linear Programming", "Genetic Algorithm"])
            st.selectbox("Objective Function", ["Minimize Cost", "Maximize Service Level", "Balance"])
            st.number_input("Planning Horizon (days)", value=30, min_value=7, max_value=365)
        
        with tabs[2]:
            st.subheader("ML Model Settings")
            st.multiselect(
                "Enabled Models",
                ["Prophet", "XGBoost", "LightGBM", "LSTM", "ARIMA"],
                default=["Prophet", "XGBoost", "LightGBM"]
            )
            st.slider("Ensemble Weights - Prophet", 0.0, 1.0, 0.3, 0.05)
            st.slider("Ensemble Weights - XGBoost", 0.0, 1.0, 0.3, 0.05)
            st.slider("Ensemble Weights - LightGBM", 0.0, 1.0, 0.4, 0.05)
        
        with tabs[3]:
            st.subheader("ERP Integrations")
            st.text_input("Beverly Knits API URL")
            st.text_input("Beverly Knits API Key", type="password")
            st.checkbox("Enable SAP Integration")
            st.checkbox("Enable Oracle NetSuite Integration")
    
    # Helper methods
    def _render_system_status(self):
        """Render system status in sidebar"""
        st.subheader("System Status")
        
        status_items = [
            ("API", "🟢 Online"),
            ("Database", "🟢 Connected"),
            ("Redis", "🟢 Active"),
            ("ML Models", "🟢 Loaded"),
            ("Celery", "🟡 3 tasks")
        ]
        
        for service, status in status_items:
            st.text(f"{service}: {status}")
    
    def _render_demand_forecast_chart(self):
        """Render demand forecast chart"""
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        forecast = pd.DataFrame({
            'Date': dates,
            'Forecast': [100 + i*2 + (i%7)*5 for i in range(30)],
            'Lower Bound': [90 + i*2 + (i%7)*5 for i in range(30)],
            'Upper Bound': [110 + i*2 + (i%7)*5 for i in range(30)]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast['Date'], y=forecast['Forecast'],
            mode='lines', name='Forecast', line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=forecast['Date'], y=forecast['Upper Bound'],
            mode='lines', name='Upper', line=dict(color='lightblue', dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=forecast['Date'], y=forecast['Lower Bound'],
            mode='lines', name='Lower', line=dict(color='lightblue', dash='dash'),
            fill='tonexty'
        ))
        
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_inventory_chart(self):
        """Render inventory levels chart"""
        categories = ['Cotton', 'Polyester', 'Buttons', 'Zippers', 'Thread']
        current = [85, 72, 90, 65, 88]
        optimal = [80, 80, 80, 80, 80]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Current', x=categories, y=current))
        fig.add_trace(go.Bar(name='Optimal', x=categories, y=optimal))
        
        fig.update_layout(
            barmode='group',
            height=300,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_recent_activities(self):
        """Render recent activities"""
        activities = [
            {"time": "2 min ago", "action": "Planning run completed", "status": "success"},
            {"time": "15 min ago", "action": "Inventory updated", "status": "info"},
            {"time": "1 hour ago", "action": "Forecast model retrained", "status": "success"},
            {"time": "3 hours ago", "action": "Supplier order placed", "status": "warning"},
            {"time": "5 hours ago", "action": "System backup completed", "status": "info"}
        ]
        
        for activity in activities:
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.text(activity["time"])
            with col2:
                st.text(activity["action"])
            with col3:
                if activity["status"] == "success":
                    st.success("✓")
                elif activity["status"] == "warning":
                    st.warning("!")
                else:
                    st.info("i")
    
    def _render_create_plan(self):
        """Render create planning form"""
        with st.form("create_plan"):
            st.subheader("Create New Planning Run")
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Plan Name", placeholder="Q1 2024 Planning")
                horizon = st.number_input("Planning Horizon (days)", value=30, min_value=7, max_value=365)
                algorithm = st.selectbox(
                    "Optimization Algorithm",
                    ["Mixed Integer", "Linear Programming", "Genetic Algorithm"]
                )
            
            with col2:
                objective = st.selectbox(
                    "Objective Function",
                    ["Minimize Cost", "Maximize Service Level", "Balance"]
                )
                confidence = st.slider("Confidence Threshold", 0.5, 1.0, 0.8, 0.05)
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            
            st.text_area("Description", placeholder="Enter planning run description...")
            
            submitted = st.form_submit_button("Start Planning Run", type="primary")
            
            if submitted:
                with st.spinner("Initializing planning run..."):
                    # Simulate API call
                    import time
                    time.sleep(2)
                    st.success(f"Planning run '{name}' started successfully!")
    
    def _render_active_plans(self):
        """Render active planning runs"""
        st.subheader("Active Planning Runs")
        
        # Sample data
        active_plans = pd.DataFrame({
            'Name': ['Q1 2024 Planning', 'Emergency Restock', 'Holiday Season Prep'],
            'Status': ['Running', 'Running', 'Queued'],
            'Progress': [65, 30, 0],
            'Started': ['10:30 AM', '11:15 AM', 'Pending'],
            'ETA': ['15 min', '45 min', '1 hour']
        })
        
        for _, plan in active_plans.iterrows():
            with st.expander(f"{plan['Name']} - {plan['Status']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Progress", f"{plan['Progress']}%")
                with col2:
                    st.metric("Started", plan['Started'])
                with col3:
                    st.metric("ETA", plan['ETA'])
                
                st.progress(plan['Progress'] / 100)
                
                if plan['Status'] == 'Running':
                    if st.button(f"Cancel {plan['Name']}", key=plan['Name']):
                        st.warning(f"Cancelling {plan['Name']}...")
    
    def _render_planning_history(self):
        """Render planning history"""
        st.subheader("Planning History")
        
        history = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=10, freq='D'),
            'Name': [f'Plan {i}' for i in range(10)],
            'Status': ['Completed'] * 8 + ['Failed', 'Cancelled'],
            'Duration': ['45 min', '32 min', '51 min', '38 min', '42 min', 
                        '35 min', '48 min', '41 min', '15 min', '5 min'],
            'Cost Savings': ['$12.3K', '$8.5K', '$15.2K', '$9.7K', '$11.4K',
                           '$7.8K', '$13.6K', '$10.2K', '-', '-']
        })
        
        st.dataframe(history, use_container_width=True)
    
    def _render_phase_monitor(self):
        """Render 6-phase monitoring"""
        st.subheader("6-Phase Planning Monitor")
        
        phases = [
            "1. Forecast Unification",
            "2. BOM Explosion",
            "3. Inventory Netting",
            "4. Procurement Optimization",
            "5. Supplier Selection",
            "6. Output Generation"
        ]
        
        progress = [100, 100, 100, 65, 0, 0]
        status = ["✅", "✅", "✅", "🔄", "⏸️", "⏸️"]
        
        for phase, prog, stat in zip(phases, progress, status):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.text(phase)
            with col2:
                st.progress(prog / 100)
            with col3:
                st.text(stat)
    
    def _render_inventory_table(self):
        """Render inventory table"""
        inventory_data = pd.DataFrame({
            'Material ID': ['MAT001', 'MAT002', 'MAT003', 'MAT004', 'MAT005'],
            'Name': ['Cotton Fabric', 'Polyester Fabric', 'Buttons', 'Zippers', 'Thread'],
            'Current Stock': [500, 300, 2000, 400, 5000],
            'Reserved': [100, 50, 500, 100, 1000],
            'Available': [400, 250, 1500, 300, 4000],
            'Reorder Point': [200, 150, 1000, 200, 2000],
            'Status': ['OK', 'OK', 'OK', 'Low', 'OK']
        })
        
        st.dataframe(
            inventory_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Inventory status",
                    width="small"
                )
            }
        )
    
    def _render_forecast_results(self):
        """Render forecast results"""
        # Generate sample forecast data
        dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
        
        fig = go.Figure()
        
        # Add traces for different models
        models = ['Prophet', 'XGBoost', 'LightGBM', 'Ensemble']
        colors = ['blue', 'green', 'orange', 'red']
        
        for model, color in zip(models, colors):
            values = [100 + i*2 + (i%7)*5 + pd.np.random.randint(-10, 10) for i in range(30)]
            fig.add_trace(go.Scatter(
                x=dates, y=values,
                mode='lines',
                name=model,
                line=dict(color=color, width=2 if model == 'Ensemble' else 1)
            ))
        
        fig.update_layout(
            title="Multi-Model Forecast Comparison",
            xaxis_title="Date",
            yaxis_title="Demand Units",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_performance_chart(self):
        """Render performance chart"""
        metrics = ['Lead Time', 'Fill Rate', 'Accuracy', 'Efficiency', 'Quality']
        current = [85, 92, 88, 91, 87]
        target = [80, 95, 90, 90, 90]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=current,
            theta=metrics,
            fill='toself',
            name='Current'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=target,
            theta=metrics,
            fill='toself',
            name='Target'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_cost_analysis(self):
        """Render cost analysis chart"""
        categories = ['Materials', 'Labor', 'Shipping', 'Storage', 'Other']
        values = [45, 25, 15, 10, 5]
        
        fig = px.pie(
            values=values,
            names=categories,
            title="Cost Breakdown",
            hole=0.4
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


# Run the application
if __name__ == "__main__":
    app = eFabUI()
    app.run()