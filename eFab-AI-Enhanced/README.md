# eFab AI Enhanced - Supply Chain Optimization Platform

## Overview
AI-powered supply chain optimization platform for textile manufacturing with 6-phase planning engine and ML-enhanced forecasting.

## Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Streamlit
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Task Queue**: Celery
- **ML**: Prophet, XGBoost, LightGBM, LSTM, ARIMA
- **Container**: Docker & Docker Compose

## Quick Start

### Using Docker (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Services will be available at:
# - API: http://localhost:8000
# - UI: http://localhost:8501
# - API Docs: http://localhost:8000/docs
```

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python scripts/setup_db.py

# Run API server
uvicorn src.api.app:app --reload --port 8000

# Run Streamlit UI (in another terminal)
streamlit run src/ui/app.py
```

## Project Structure
```
eFab-AI-Enhanced/
├── src/
│   ├── api/           # FastAPI backend
│   ├── core/          # Business logic
│   ├── database/      # Data models
│   ├── engine/        # Planning & ML engines
│   ├── agents/        # Multi-agent system
│   └── ui/            # Streamlit frontend
├── tests/             # Test suite
├── docker/            # Docker configurations
└── docs/              # Documentation
```

## Features
- 6-Phase Planning Engine
- ML-Enhanced Demand Forecasting
- ERP Integration (Beverly Knits, SAP, Oracle, etc.)
- Real-time Analytics Dashboard
- Multi-Agent Autonomous Planning
- JWT Authentication & RBAC

## Documentation
See [COMPREHENSIVE_DOCUMENTATION.md](../spec/COMPREHENSIVE_DOCUMENTATION.md) for detailed technical documentation.

## License
Proprietary - All rights reserved