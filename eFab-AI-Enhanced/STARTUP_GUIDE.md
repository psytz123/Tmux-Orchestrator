# eFab AI Enhanced - Startup Guide

## 🚀 Quick Start with Real ERP Data

The application is now fully integrated with Beverly Knits ERP data, processing real inventory, sales orders, and yarn demand forecasts.

### Data Statistics
- **23,250** inventory records across 4 warehouses
- **149** active sales orders worth **$1.76M**
- **188** yarn demand forecast records
- **Top Customers**: Sears Manufacturing, WL GORE, Purple Innovations

## 📊 Starting the Application

### Option 1: Docker (Recommended)
```bash
cd /mnt/c/Users/psytz/TMUX\ Final/Tmux-Orchestrator/eFab-AI-Enhanced

# Start all services
./start.sh

# Or manually
docker-compose up --build
```

### Option 2: Local Development
```bash
# Terminal 1 - API Server
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.api.app:app --reload --port 8000

# Terminal 2 - Streamlit UI
source venv/bin/activate
streamlit run src/ui/app.py
```

## 🌐 Access Points

- **Streamlit UI**: http://localhost:8501
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Flower (Celery)**: http://localhost:5555

## 📈 Key Features with Real Data

### 1. ERP Data Dashboard
Navigate to **🗄️ ERP Data** in the UI to see:
- Real-time inventory levels by warehouse
- Active sales orders with customer details
- Yarn demand forecasts by week
- Analytics and coverage ratios

### 2. Planning with Real Data
The **📊 Planning** page now uses:
- Actual Beverly Knits inventory levels
- Real customer orders and demand
- Historical yarn consumption patterns
- Supplier lead times from ERP

### 3. Inventory Management
The **📦 Inventory** page shows:
- Current stock across F01, G00, I01, P01 warehouses
- Critical items with low stock
- Reorder recommendations
- Warehouse distribution charts

### 4. Demand Forecasting
The **📈 Forecasting** page provides:
- ML-enhanced predictions based on real yarn demand
- Weekly forecasts for production planning
- Style-based demand breakdown
- Confidence scores based on data quality

## 🔧 Testing ERP Integration

Verify the ERP data is loading correctly:
```bash
python3 test_erp_data.py
```

Expected output:
- ✅ 23,250 inventory records
- ✅ 149 sales orders
- ✅ $1.76M total order value
- ✅ 4 warehouses active

## 📁 ERP Data Files Location

Real data files are located at:
```
/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/ERP Data/
```

Includes:
- `eFab_Inventory_*.csv` - Warehouse inventory
- `eFab_SO_List_*.csv` - Sales orders
- `Yarn_Demand_*.csv` - Demand forecasts
- `yarn_inventory*.xlsx` - Yarn stock levels

## 🎯 6-Phase Planning Engine

The planning engine now processes real data through:

1. **Forecast Unification** - Uses actual yarn demand data
2. **BOM Explosion** - Based on real product structures
3. **Inventory Netting** - Current Beverly Knits stock levels
4. **Procurement Optimization** - Optimizes based on real costs
5. **Supplier Selection** - Uses actual vendor information
6. **Output Generation** - Creates actionable reports

## 🔄 Data Refresh

To update with latest ERP data:
1. Go to **🗄️ ERP Data** → **Data Sync** tab
2. Click **🔄 Refresh All Data**
3. Or enable Auto-Sync for periodic updates

## 📊 Key Metrics Dashboard

The main dashboard displays:
- **Inventory Health**: 87% (based on coverage ratio)
- **Forecast Accuracy**: Using ML models on real data
- **Cost Savings**: Calculated from optimization
- **Active Planning Runs**: Real-time status

## 🛠️ Troubleshooting

### Data Not Loading
```bash
# Check data files exist
ls -la "/mnt/c/Users/psytz/TMUX Final/Tmux-Orchestrator/ERP Data/"

# Test loader directly
python3 -c "from src.data.erp_loader import ERPDataLoader; loader = ERPDataLoader(); print(loader.load_all_data()['summary'])"
```

### UI Not Displaying Data
1. Check browser console for errors
2. Verify API is running: http://localhost:8000/health
3. Clear browser cache and refresh

### Planning Engine Issues
1. Check logs: `docker-compose logs api`
2. Verify database connection
3. Ensure Redis is running for task queue

## 📈 Next Steps

1. **Configure ML Models**: Train on your historical data
2. **Set Up Alerts**: Configure thresholds for critical items
3. **Customize Reports**: Modify output templates
4. **Add ERP Connectors**: Direct integration with Beverly Knits API
5. **Schedule Planning Runs**: Set up automated daily/weekly runs

## 📞 Support

For issues or questions about the eFab AI Enhanced platform:
- Check logs: `docker-compose logs -f`
- API health: http://localhost:8000/health
- Test data integration: `python3 test_erp_data.py`

---

**Version**: 2.0.0  
**Data Source**: Beverly Knits ERP System  
**Last Updated**: 2024