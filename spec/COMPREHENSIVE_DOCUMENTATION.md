# eFab AI Enhanced - Comprehensive Technical Documentation

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Quick Start Guide](#2-quick-start-guide)
3. [Architecture Overview](#3-architecture-overview)
4. [API Documentation](#4-api-documentation)
5. [Database Schema](#5-database-schema)
6. [Feature Documentation](#6-feature-documentation)
7. [Development Guide](#7-development-guide)
8. [Deployment & Operations](#8-deployment--operations)
9. [Security Implementation](#9-security-implementation)
10. [Performance & Optimization](#10-performance--optimization)
11. [Testing Strategy](#11-testing-strategy)
12. [Troubleshooting](#12-troubleshooting)
13. [Technical Roadmap](#13-technical-roadmap)

---

## 1. Executive Summary

### Project Overview

**eFab AI Enhanced** is a sophisticated AI-powered supply chain optimization platform specifically designed for textile manufacturing operations. Version 2.0.0 represents a complete architectural evolution from the original monolithic Streamlit application to a microservices-based platform with enhanced scalability, reliability, and performance.

### Key Features

- **6-Phase Planning Engine**: Forecast Unification → BOM Explosion → Inventory Netting → Procurement Optimization → Supplier Selection → Output Generation
- **ML-Enhanced Forecasting**: Multi-model ensemble (Prophet, XGBoost, LightGBM, LSTM, ARIMA) with intelligent fallback mechanisms
- **ERP Integration**: Native Beverly Knits integration with SAP, Oracle NetSuite, Microsoft Dynamics, Epicor connectors
- **Multi-Agent System**: Distributed agent architecture for autonomous planning and optimization
- **Real-time Analytics**: Live dashboard with performance monitoring and predictive insights
- **Advanced Authentication**: JWT-based security with role-based access control

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Backend API** | FastAPI | 0.104.1 |
| **Frontend UI** | Streamlit | 1.28.2 |
| **Database** | PostgreSQL | 16 |
| **Cache/Messaging** | Redis | 7 |
| **Task Queue** | Celery | 5.3.0 |
| **ML Framework** | Multiple (scikit-learn, Prophet, XGBoost, TensorFlow, PyTorch) | Latest |
| **Container** | Docker + Docker Compose | Latest |
| **Language** | Python | 3.11+ |

### Architecture Type

**Domain-Driven Design (DDD)** with **Clean Architecture** principles:
- Clear separation of concerns
- Dependency inversion
- Microservices-ready structure
- Event-driven communication patterns

---

## 2. Quick Start Guide

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16+ (if running locally)
- Redis 7+ (if running locally)
- Git

### Installation & Setup

#### Option 1: Docker Deployment (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd efab-ai-enhanced

# Setup environment
make setup-env  # Creates .env from .env.example

# Start all services
make docker-up

# Check service health
docker-compose ps
```

Services will be available at:
- **API**: http://localhost:8000
- **UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Flower (Task Monitor)**: http://localhost:5555

#### Option 2: Local Development Setup

```bash
# Install dependencies
make install-all

# Setup database
make dev-db-start
make db-upgrade

# Setup Redis
make dev-redis-start

# Start services
make run-all  # Starts API, UI, and worker processes
```

### Essential Commands

```bash
# Development
make install-all      # Install all dependencies
make run-api         # Start FastAPI server
make run-ui          # Start Streamlit UI
make run-worker      # Start Celery worker

# Testing
make test            # Run all tests
make test-cov        # Run with coverage (80% minimum)
make lint            # Run code quality checks
make format          # Format code

# Database
make db-upgrade      # Apply migrations
make db-reset        # Reset database
make db-create-migration message="description"

# ML Operations
make train-models    # Train ML models
make evaluate-models # Evaluate model performance

# Quality Assurance
make quality         # Run all quality checks
make security-check  # Run security analysis
```

### Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://efab_user:efab_password@localhost:5432/efab_ai_enhanced
REDIS_URL=redis://localhost:6379/0

# ML Configuration
ML_ENABLED=true
ML_CONFIDENCE_THRESHOLD=0.6
ML_FALLBACK_CONFIDENCE_THRESHOLD=0.7

# ERP Integration
ERP_BASE_URL=https://efab.bkiapps.com
ERP_API_KEY=your-api-key

# Security
JWT_SECRET_KEY=your-secret-key
SESSION_TIMEOUT_MINUTES=30
```

---

## 3. Architecture Overview

### System Topology

```mermaid
graph TB
    subgraph "External Systems"
        ERP[ERP Systems]
        MCP[MCP Clients]
    end
    
    subgraph "Load Balancer"
        LB[Nginx]
    end
    
    subgraph "Application Layer"
        API[FastAPI API]
        UI[Streamlit UI]
        WORKER[Celery Workers]
    end
    
    subgraph "Agent System"
        COORD[Coordinator]
        DATA_AGENT[Data Agent]
        ML_AGENT[ML Agent]
        PLAN_AGENT[Planning Agent]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL)]
        CACHE[(Redis)]
        FILES[File Storage]
    end
    
    subgraph "ML/AI Layer"
        MODELS[ML Models]
        ENSEMBLE[Ensemble Engine]
        FALLBACK[Fallback Models]
    end
    
    ERP --> MCP
    MCP --> API
    LB --> API
    LB --> UI
    API --> WORKER
    API --> COORD
    COORD --> DATA_AGENT
    COORD --> ML_AGENT
    COORD --> PLAN_AGENT
    API --> DB
    API --> CACHE
    WORKER --> DB
    WORKER --> CACHE
    ML_AGENT --> MODELS
    ML_AGENT --> ENSEMBLE
    ENSEMBLE --> FALLBACK
```

### Core Components

#### 1. API Layer (`src/api/`)
- **FastAPI Application**: RESTful API with automatic OpenAPI documentation
- **Middleware**: CORS, compression, authentication, rate limiting
- **Routers**: Modular endpoint organization by domain
- **WebSocket Support**: Real-time communication capabilities

#### 2. Domain Layer (`src/core/`)
- **Domain Models**: Business entities and value objects
- **Use Cases**: Business logic implementation
- **Interfaces**: Contracts for external dependencies
- **Configuration**: Centralized settings management

#### 3. Data Layer (`src/database/`)
- **Models**: SQLAlchemy ORM models
- **Repositories**: Data access abstraction
- **Migrations**: Database schema versioning
- **Seeds**: Test and initial data

#### 4. Engine Layer (`src/engine/`)
- **Planning Engine**: 6-phase optimization process
- **ML Engine**: Multi-model forecasting and prediction
- **Monitoring**: Performance tracking and alerting

#### 5. Agent System (`src/agents/`)
- **Base Agent**: Abstract agent with lifecycle management
- **Specialized Agents**: Domain-specific autonomous agents
- **Coordinator**: Agent orchestration and communication
- **Message Bus**: Inter-agent communication

### Data Flow Patterns

#### Planning Workflow
```
1. Input Data Collection → ERP Integration → Data Validation
2. Forecast Generation → ML Model Selection → Ensemble Prediction
3. Planning Phases → BOM → Inventory → Procurement → Supplier → Output
4. Result Generation → Recommendations → Monitoring
```

#### ML Model Selection Flow
```
Historical Data → Model Training → Confidence Assessment
├─ Confidence > 80% → Advanced ML Models
├─ Confidence 60-80% → Ensemble Methods  
├─ Confidence < 60% → Statistical Fallback
└─ No Data → Simple Moving Average
```

---

## 4. API Documentation

### Authentication

All API endpoints require authentication via JWT tokens:

```bash
# Obtain token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/planning/runs"
```

### Core Endpoints

#### Planning API

##### Create Planning Run
```http
POST /api/v1/planning/runs
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Q1 2024 Planning",
  "description": "Quarterly planning run",
  "horizon_days": 90,
  "configuration": {
    "enable_ml_forecasting": true,
    "consolidation_window_days": 7
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Q1 2024 Planning",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z",
  "horizon_days": 90
}
```

##### Get Planning Run Status
```http
GET /api/v1/planning/runs/{run_id}/status
```

**Response:**
```json
{
  "planning_run_id": "uuid",
  "overall_status": "running",
  "current_phase": "forecast_unification",
  "phases": {
    "forecast_unification": {
      "status": "completed",
      "duration": 45.2,
      "metrics": {"processed_records": 1500},
      "warnings": 0,
      "errors": 0
    },
    "bom_explosion": {
      "status": "running",
      "progress": 65
    }
  }
}
```

#### Inventory API

##### Get Inventory Levels
```http
GET /api/v1/inventory/materials?warehouse_id=WH001&category=raw_material
```

**Response:**
```json
{
  "materials": [
    {
      "material_id": "MTL001",
      "material_name": "Cotton Yarn",
      "current_stock": 1500.0,
      "available_stock": 1200.0,
      "safety_stock": 200.0,
      "reorder_point": 300.0,
      "unit_of_measure": "KG",
      "warehouse_id": "WH001"
    }
  ],
  "total_count": 150,
  "page": 1,
  "per_page": 20
}
```

#### Forecasting API

##### Generate Forecast
```http
POST /api/v1/forecasting/generate
Content-Type: application/json

{
  "product_ids": ["PROD001", "PROD002"],
  "horizon_days": 30,
  "model_type": "ensemble",
  "confidence_threshold": 0.8
}
```

**Response:**
```json
{
  "forecast_id": "uuid",
  "status": "completed",
  "results": [
    {
      "product_id": "PROD001",
      "forecasts": [
        {
          "date": "2024-01-01",
          "quantity": 150.5,
          "confidence": 0.85,
          "model_used": "prophet"
        }
      ],
      "accuracy_metrics": {
        "mae": 12.5,
        "mape": 8.3,
        "rmse": 18.7
      }
    }
  ]
}
```

#### Supplier API

##### Get Supplier Recommendations
```http
GET /api/v1/suppliers/recommendations?material_id=MTL001&quantity=1000
```

**Response:**
```json
{
  "recommendations": [
    {
      "supplier_id": "SUP001",
      "supplier_name": "Best Textiles Ltd",
      "score": 0.92,
      "factors": {
        "price": 0.85,
        "quality": 0.95,
        "lead_time": 0.90,
        "reliability": 0.98
      },
      "unit_price": 9.50,
      "lead_time_days": 14,
      "minimum_order_quantity": 500
    }
  ]
}
```

### WebSocket Endpoints

#### Real-time Planning Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/planning/runs/{run_id}');

ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('Phase update:', update);
};
```

### Error Handling

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "horizon_days",
      "issue": "must be between 1 and 365"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
  }
}
```

### Rate Limiting

API endpoints are rate-limited:
- **General endpoints**: 100 requests/minute
- **Planning operations**: 10 requests/minute
- **Authentication**: 5 requests/minute

---

## 5. Database Schema

### Core Tables

#### Materials Inventory
```sql
CREATE TABLE materials_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id VARCHAR(100) UNIQUE NOT NULL,
    material_name VARCHAR(255) NOT NULL,
    material_type material_type_enum NOT NULL,
    sku VARCHAR(100) UNIQUE,
    category VARCHAR(100),
    current_stock DECIMAL(15,3) NOT NULL DEFAULT 0,
    reserved_stock DECIMAL(15,3) NOT NULL DEFAULT 0,
    available_stock DECIMAL(15,3) NOT NULL DEFAULT 0,
    safety_stock DECIMAL(15,3) NOT NULL DEFAULT 0,
    reorder_point DECIMAL(15,3) NOT NULL DEFAULT 0,
    reorder_quantity DECIMAL(15,3) NOT NULL DEFAULT 0,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'EA',
    unit_cost DECIMAL(15,3),
    lead_time_days INTEGER NOT NULL DEFAULT 7,
    warehouse_id VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_current_stock_positive CHECK (current_stock >= 0),
    CONSTRAINT check_reserved_stock_positive CHECK (reserved_stock >= 0),
    CONSTRAINT check_available_stock_positive CHECK (available_stock >= 0)
);

CREATE INDEX idx_materials_inventory_material_id ON materials_inventory(material_id);
CREATE INDEX idx_materials_inventory_category ON materials_inventory(category);
CREATE INDEX idx_materials_inventory_warehouse ON materials_inventory(warehouse_id);
```

#### Planning Runs
```sql
CREATE TABLE planning_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status planning_status_enum NOT NULL DEFAULT 'pending',
    planning_horizon_days INTEGER NOT NULL DEFAULT 30,
    optimization_algorithm VARCHAR(100) NOT NULL DEFAULT 'mixed_integer',
    objective_function VARCHAR(100) NOT NULL DEFAULT 'minimize_cost',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_time_seconds DECIMAL(10,3),
    total_cost DECIMAL(15,2),
    total_revenue DECIMAL(15,2),
    service_level DECIMAL(5,2),
    input_parameters JSONB,
    optimization_results JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_planning_runs_status ON planning_runs(status);
CREATE INDEX idx_planning_runs_created_at ON planning_runs(created_at);
```

#### Inventory Transactions
```sql
CREATE TABLE inventory_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id VARCHAR(100) NOT NULL,
    transaction_type transaction_type_enum NOT NULL,
    quantity DECIMAL(15,3) NOT NULL,
    unit_cost DECIMAL(15,3),
    total_cost DECIMAL(15,2),
    reference_type VARCHAR(50),
    reference_number VARCHAR(100),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stock_before DECIMAL(15,3),
    stock_after DECIMAL(15,3),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_transactions_material ON inventory_transactions(material_id);
CREATE INDEX idx_inventory_transactions_date ON inventory_transactions(transaction_date);
CREATE INDEX idx_inventory_transactions_type ON inventory_transactions(transaction_type);
```

### Relationships

```mermaid
erDiagram
    PLANNING_RUNS ||--o{ PRODUCTION_SCHEDULES : has
    PLANNING_RUNS ||--o{ FORECASTS : generates
    MATERIALS_INVENTORY ||--o{ INVENTORY_TRANSACTIONS : tracks
    MATERIALS_INVENTORY ||--o{ STOCK_SNAPSHOTS : daily_snapshots
    
    PLANNING_RUNS {
        uuid id PK
        varchar name
        planning_status_enum status
        integer planning_horizon_days
        timestamp started_at
        timestamp completed_at
        jsonb optimization_results
    }
    
    PRODUCTION_SCHEDULES {
        uuid id PK
        uuid planning_run_id FK
        varchar product_id
        timestamp scheduled_date
        decimal quantity
        schedule_status_enum status
    }
    
    MATERIALS_INVENTORY {
        uuid id PK
        varchar material_id UK
        varchar material_name
        material_type_enum material_type
        decimal current_stock
        decimal safety_stock
        decimal reorder_point
    }
    
    INVENTORY_TRANSACTIONS {
        uuid id PK
        varchar material_id FK
        transaction_type_enum transaction_type
        decimal quantity
        timestamp transaction_date
    }
```

### Database Indexes

Performance-optimized indexes:

```sql
-- Composite indexes for common queries
CREATE INDEX idx_materials_category_active ON materials_inventory(category, is_active);
CREATE INDEX idx_transactions_material_date ON inventory_transactions(material_id, transaction_date);
CREATE INDEX idx_planning_status_created ON planning_runs(status, created_at);

-- Partial indexes for active records
CREATE INDEX idx_materials_active ON materials_inventory(material_id) WHERE is_active = true;

-- Expression indexes for calculations
CREATE INDEX idx_inventory_available_stock ON materials_inventory((current_stock - reserved_stock));
```

### Data Migration Strategy

```bash
# Create migration
make db-create-migration message="add_material_categories"

# Apply migrations
make db-upgrade

# Rollback if needed
alembic downgrade -1
```

---

## 6. Feature Documentation

### 6.1 Planning Engine

The planning engine orchestrates a 6-phase optimization process designed for textile manufacturing supply chains.

#### Phase 1: Forecast Unification
**Purpose**: Consolidate demand forecasts from multiple sources with reliability weighting.

**Implementation**: `src/engine/planning/phases/forecast_unification.py`

```python
class ForecastUnificationPhase(BasePhase):
    async def execute(self, context: PhaseContext) -> Dict[str, Any]:
        # 1. Collect forecasts from multiple sources
        forecasts = await self._collect_forecasts(context)
        
        # 2. Apply source reliability weights
        weighted_forecasts = self._apply_source_weights(forecasts)
        
        # 3. Resolve conflicts and consolidate
        unified_forecast = self._consolidate_forecasts(weighted_forecasts)
        
        return {
            "unified_demand_forecast": unified_forecast,
            "source_weights": self.source_weights,
            "consolidation_metrics": self._calculate_metrics()
        }
```

**Key Features**:
- Multiple data source integration (ERP, CSV, manual input)
- Confidence-based weighting algorithms
- Conflict resolution for overlapping forecasts
- Automatic data quality validation

#### Phase 2: BOM Explosion
**Purpose**: Convert SKU-level forecasts to material requirements using Bill of Materials.

**Implementation**: `src/engine/planning/phases/bom_explosion.py`

```python
async def explode_bom(self, product_forecast: Dict) -> List[MaterialRequirement]:
    """Multi-level BOM explosion with yield factors"""
    requirements = []
    
    for product_id, forecast_qty in product_forecast.items():
        bom = await self._get_bom(product_id)
        
        # Recursive explosion for multi-level BOMs
        exploded = await self._recursive_explode(
            bom, forecast_qty, level=0
        )
        requirements.extend(exploded)
    
    return self._consolidate_requirements(requirements)
```

#### Phase 3: Inventory Netting
**Purpose**: Account for current inventory levels and in-transit materials.

**Key Calculations**:
- **Gross Requirements**: From BOM explosion
- **On-Hand Inventory**: Current stock levels
- **Scheduled Receipts**: Purchase orders and production orders
- **Net Requirements**: Gross - On-Hand - Scheduled + Safety Stock

#### Phase 4: Procurement Optimization
**Purpose**: Apply Economic Order Quantity (EOQ) and optimize purchase quantities.

**Algorithms**:
- Classic EOQ with carrying cost optimization
- Quantity break analysis for volume discounts
- Lead time variability consideration
- Multi-period consolidation

#### Phase 5: Supplier Selection
**Purpose**: Multi-criteria supplier scoring and allocation.

**Scoring Factors** (configurable weights):
```python
DEFAULT_WEIGHTS = {
    "price": 0.3,           # Cost competitiveness
    "lead_time": 0.2,       # Delivery speed
    "quality": 0.2,         # Quality metrics
    "reliability": 0.2,     # On-time delivery
    "relationship": 0.1     # Strategic partnership
}
```

#### Phase 6: Output Generation
**Purpose**: Generate final recommendations and risk assessments.

**Outputs**:
- Purchase order recommendations
- Supplier allocation strategies
- Risk assessment matrix
- Performance projections

### 6.2 ML Forecasting System

#### Multi-Model Ensemble Architecture

The system employs multiple forecasting models with intelligent selection:

```python
class EnsembleForecaster:
    def __init__(self):
        self.models = {
            'prophet': ProphetModel(),
            'xgboost': XGBoostModel(),
            'lightgbm': LightGBMModel(),
            'lstm': LSTMModel(),
            'arima': ARIMAModel()
        }
        self.fallback_models = {
            'moving_average': MovingAverageModel(),
            'exponential_smoothing': ExponentialSmoothingModel(),
            'seasonal': SeasonalNaiveModel()
        }
```

#### Model Selection Logic

```python
async def select_best_model(self, data: DataFrame) -> str:
    """Intelligent model selection based on data characteristics"""
    
    # Data quality assessment
    quality_score = self._assess_data_quality(data)
    
    # Pattern detection
    patterns = self._detect_patterns(data)
    
    # Model suitability scoring
    model_scores = {}
    for model_name, model in self.models.items():
        score = self._score_model_suitability(
            model, data, patterns, quality_score
        )
        model_scores[model_name] = score
    
    # Select best model or ensemble
    if max(model_scores.values()) > self.confidence_threshold:
        return max(model_scores, key=model_scores.get)
    else:
        return self._create_ensemble(model_scores)
```

#### Fallback Mechanism

When ML models fail or have low confidence:

1. **Confidence < 60%**: Use statistical fallback methods
2. **No historical data**: Simple moving average
3. **Data quality issues**: Exponential smoothing
4. **Seasonal patterns detected**: Seasonal naive model

### 6.3 ERP Integration

#### Beverly Knits Native Integration

Direct integration with Beverly Knits ERP system:

```python
class BeverlyKnitsERPClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.session = httpx.AsyncClient()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    async def sync_inventory(self) -> List[InventoryItem]:
        """Sync inventory data from Beverly Knits ERP"""
        response = await self.session.get(f"{self.base_url}/api/inventory")
        return [InventoryItem(**item) for item in response.json()]
```

#### Universal ERP Connectors

Support for major ERP systems:
- **SAP**: via RFC/BAPI and REST APIs
- **Oracle NetSuite**: RESTlet integration
- **Microsoft Dynamics**: OData endpoints
- **Epicor**: REST API with authentication

#### Data Mapping and Validation

```python
class ERPDataMapper:
    """Universal data mapping for different ERP systems"""
    
    MAPPING_SCHEMAS = {
        'sap': {
            'material_id': 'MATNR',
            'material_name': 'MAKTX',
            'stock_quantity': 'LABST'
        },
        'netsuite': {
            'material_id': 'item.internalid',
            'material_name': 'item.displayname',
            'stock_quantity': 'quantityavailable'
        }
    }
```

### 6.4 Multi-Agent System

#### Agent Types and Responsibilities

1. **Data Integration Agent**: ERP synchronization and data quality
2. **ML Model Agent**: Model training and inference
3. **Planning Agent**: Optimization and scheduling
4. **Monitoring Agent**: Performance tracking and alerting

#### Agent Communication

```python
class AgentMessage(BaseModel):
    sender_id: str
    recipient_id: Optional[str]
    message_type: MessageType
    payload: Dict[str, Any]
    correlation_id: Optional[str]
    timestamp: datetime
    priority: Priority = Priority.NORMAL
```

#### Agent Lifecycle Management

```python
class BaseAgent(ABC):
    async def start(self) -> None:
        """Initialize and start agent"""
        await self._initialize()
        self._main_task = asyncio.create_task(self._run())
        self.state = AgentState.IDLE
    
    async def _run(self) -> None:
        """Main agent loop"""
        while self.is_running:
            message = await self._message_queue.get()
            await self._process_message(message)
```

---

## 7. Development Guide

### 7.1 Environment Setup

#### Development Prerequisites

```bash
# Python version
python --version  # Should be 3.11+

# Install Poetry (dependency management)
curl -sSL https://install.python-poetry.org | python3 -

# Install system dependencies
sudo apt-get update
sudo apt-get install -y postgresql-client redis-tools
```

#### Project Setup

```bash
# Clone and setup
git clone <repository-url>
cd efab-ai-enhanced

# Install dependencies
make install-all

# Setup pre-commit hooks
make setup-dev

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

#### IDE Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.linting.mypyEnabled": true
}
```

### 7.2 Code Standards

#### Code Style

The project follows **Black** code formatting with these specifications:
- Line length: 88 characters
- Python 3.11+ syntax
- Type hints required
- Docstrings in Google format

#### Linting Configuration

```toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings  
    "F",    # pyflakes
    "I",    # isort
    "C",    # flake8-comprehensions
    "B",    # flake8-bugbear
]
```

#### Type Checking

```python
# Example of proper type annotations
from typing import List, Optional, Dict, Any
from decimal import Decimal

async def process_inventory(
    items: List[InventoryItem],
    warehouse_id: Optional[str] = None
) -> Dict[str, Any]:
    """Process inventory items with optional warehouse filtering.
    
    Args:
        items: List of inventory items to process
        warehouse_id: Optional warehouse filter
        
    Returns:
        Processing results with metrics
        
    Raises:
        ValidationError: If items are invalid
    """
    results: Dict[str, Any] = {}
    # Implementation...
    return results
```

### 7.3 Project Structure

```
efab-ai-enhanced/
├── src/                          # Source code
│   ├── api/                      # FastAPI application
│   │   ├── app.py               # Main app instance
│   │   ├── routers/             # API route handlers
│   │   └── middleware/          # Custom middleware
│   ├── core/                    # Core business logic
│   │   ├── config.py            # Configuration management
│   │   ├── constants.py         # Application constants
│   │   ├── domain/              # Domain models
│   │   ├── interfaces/          # Abstract interfaces
│   │   └── use_cases/           # Business use cases
│   ├── database/                # Data layer
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/        # Data access layer
│   │   ├── migrations/          # Database migrations
│   │   └── seeds/               # Test data
│   ├── engine/                  # Planning and ML engines
│   │   ├── planning/            # Planning engine phases
│   │   ├── ml/                  # ML models and training
│   │   └── forecasting/         # Forecasting models
│   ├── agents/                  # Multi-agent system
│   │   ├── base/                # Base agent classes
│   │   ├── specialized/         # Domain-specific agents
│   │   └── communication/       # Message passing
│   ├── data/                    # Data integration
│   │   ├── connectors/          # ERP connectors
│   │   ├── validators/          # Data validation
│   │   └── transformers/        # Data transformation
│   ├── ui/                      # Streamlit interface
│   │   ├── app.py               # Main UI app
│   │   ├── pages/               # UI pages
│   │   └── components/          # Reusable components
│   └── utils/                   # Utility functions
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── performance/             # Performance tests
│   └── fixtures/                # Test fixtures
├── docker/                      # Docker configurations
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── models/                      # Trained ML models
├── data/                        # Data storage
└── config/                      # Configuration files
```

### 7.4 Adding New Features

#### Creating a New API Endpoint

1. **Define the router**:
```python
# src/api/routers/new_feature.py
from fastapi import APIRouter, Depends
from src.core.use_cases.new_feature_service import NewFeatureService

router = APIRouter(prefix="/new-feature", tags=["new-feature"])

@router.post("/action")
async def perform_action(
    request: ActionRequest,
    service: NewFeatureService = Depends()
):
    """Perform new feature action."""
    result = await service.perform_action(request)
    return {"success": True, "result": result}
```

2. **Implement the use case**:
```python
# src/core/use_cases/new_feature_service.py
from abc import ABC, abstractmethod

class NewFeatureService:
    def __init__(self, repository: NewFeatureRepository):
        self.repository = repository
    
    async def perform_action(self, request: ActionRequest) -> ActionResult:
        # Business logic implementation
        pass
```

3. **Add to main app**:
```python
# src/api/app.py
from src.api.routers import new_feature

app.include_router(new_feature.router, prefix="/api/v1")
```

#### Adding Database Models

1. **Create the model**:
```python
# src/database/models/new_model.py
from sqlalchemy import Column, String, Integer
from src.database.base import BaseModel

class NewModel(BaseModel):
    __tablename__ = "new_models"
    
    name = Column(String(255), nullable=False)
    value = Column(Integer, nullable=False, default=0)
```

2. **Create migration**:
```bash
make db-create-migration message="add_new_model_table"
```

3. **Apply migration**:
```bash
make db-upgrade
```

### 7.5 Testing Guidelines

#### Test Structure

```python
# tests/unit/test_new_feature.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.core.use_cases.new_feature_service import NewFeatureService

class TestNewFeatureService:
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        return NewFeatureService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_perform_action_success(self, service, mock_repository):
        # Arrange
        mock_repository.get_data.return_value = "test_data"
        request = ActionRequest(param="value")
        
        # Act
        result = await service.perform_action(request)
        
        # Assert
        assert result.success is True
        mock_repository.get_data.assert_called_once()
```

#### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/unit/test_new_feature.py -v

# With coverage
make test-cov

# Performance tests
make test-performance

# Integration tests
make test-integration
```

---

## 8. Deployment & Operations

### 8.1 Docker Deployment

#### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
      POSTGRES_DB: ${DATABASE_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - efab-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - efab-network
    restart: unless-stopped

  api:
    build:
      context: .
      dockerfile: docker/app/Dockerfile
    environment:
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - postgres
      - redis
    networks:
      - efab-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
      - ui
    networks:
      - efab-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  efab-network:
    driver: bridge
```

#### Deployment Commands

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# View logs
docker-compose -f docker-compose.prod.yml logs -f api

# Database backup
docker exec efab-postgres pg_dump -U efab_user efab_ai_enhanced > backup.sql
```

### 8.2 Kubernetes Deployment

#### Namespace and ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: efab-ai-enhanced

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: efab-config
  namespace: efab-ai-enhanced
data:
  DATABASE_HOST: postgres-service
  REDIS_HOST: redis-service
  ENVIRONMENT: production
```

#### Application Deployment

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: efab-api
  namespace: efab-ai-enhanced
spec:
  replicas: 3
  selector:
    matchLabels:
      app: efab-api
  template:
    metadata:
      labels:
        app: efab-api
    spec:
      containers:
      - name: api
        image: efab-ai-enhanced:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: efab-secrets
              key: database-url
        envFrom:
        - configMapRef:
            name: efab-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### 8.3 Monitoring & Observability

#### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'efab-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
```

#### Grafana Dashboards

Key metrics to monitor:
- **API Performance**: Response times, error rates, throughput
- **Database**: Connection pool, query performance, deadlocks
- **ML Models**: Prediction accuracy, inference time, model drift
- **Planning Engine**: Phase execution times, success rates
- **System Resources**: CPU, memory, disk usage

#### Application Metrics

```python
# src/utils/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# API metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# Planning metrics
planning_runs_total = Counter(
    'planning_runs_total',
    'Total planning runs',
    ['status']
)

ml_model_accuracy = Gauge(
    'ml_model_accuracy',
    'ML model accuracy',
    ['model_name', 'product_id']
)
```

### 8.4 Backup & Recovery

#### Database Backup Strategy

```bash
#!/bin/bash
# scripts/backup_database.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="efab_ai_enhanced"

# Create backup
pg_dump -h postgres -U efab_user -d $DB_NAME > \
  "$BACKUP_DIR/efab_backup_$TIMESTAMP.sql"

# Compress backup
gzip "$BACKUP_DIR/efab_backup_$TIMESTAMP.sql"

# Keep only last 30 days
find $BACKUP_DIR -name "efab_backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/efab_backup_$TIMESTAMP.sql.gz" \
  s3://efab-backups/database/
```

#### ML Model Versioning

```python
# src/ml/model_registry.py
class ModelRegistry:
    def save_model(self, model, model_name: str, version: str):
        """Save model with versioning"""
        model_path = f"models/{model_name}/v{version}"
        
        # Save model artifacts
        joblib.dump(model, f"{model_path}/model.pkl")
        
        # Save metadata
        metadata = {
            "name": model_name,
            "version": version,
            "created_at": datetime.utcnow().isoformat(),
            "metrics": model.get_metrics(),
            "parameters": model.get_params()
        }
        
        with open(f"{model_path}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
```

---

## 9. Security Implementation

### 9.1 Authentication & Authorization

#### JWT Authentication Flow

```python
# src/auth/jwt_manager.py
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise JWTError("Token missing subject")
            return email
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
```

#### Role-Based Access Control

```python
# src/auth/permissions.py
from enum import Enum
from functools import wraps

class Role(Enum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    MANAGER = "manager"
    ADMIN = "admin"

class Permission(Enum):
    VIEW_DASHBOARD = "view_dashboard"
    RUN_PLANNING = "run_planning"
    MANAGE_INVENTORY = "manage_inventory"
    ADMIN_USERS = "admin_users"

ROLE_PERMISSIONS = {
    Role.VIEWER: [Permission.VIEW_DASHBOARD],
    Role.ANALYST: [Permission.VIEW_DASHBOARD, Permission.RUN_PLANNING],
    Role.MANAGER: [
        Permission.VIEW_DASHBOARD,
        Permission.RUN_PLANNING,
        Permission.MANAGE_INVENTORY
    ],
    Role.ADMIN: list(Permission)  # All permissions
}

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if not has_permission(current_user.role, permission):
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 9.2 Data Security

#### Encryption at Rest

```python
# src/security/encryption.py
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data like API keys"""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
```

#### SQL Injection Prevention

All database queries use parameterized statements:

```python
# Good: Using SQLAlchemy ORM
async def get_material_by_id(material_id: str):
    query = select(MaterialsInventory).where(
        MaterialsInventory.material_id == material_id
    )
    return await session.execute(query)

# Good: Using raw SQL with parameters
async def get_inventory_summary(warehouse_id: str):
    query = text("""
        SELECT material_type, SUM(current_stock)
        FROM materials_inventory 
        WHERE warehouse_id = :warehouse_id
        GROUP BY material_type
    """)
    return await session.execute(query, {"warehouse_id": warehouse_id})
```

### 9.3 API Security

#### Rate Limiting

```python
# src/api/middleware/rate_limiter.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.state.limiter = limiter
@app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/planning/runs")
@limiter.limit("10/minute")  # Limit planning runs
async def create_planning_run(request: Request, ...):
    # Implementation
    pass
```

#### Input Validation

```python
# src/api/models/validation.py
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class CreatePlanningRunRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    horizon_days: int = Field(..., ge=1, le=365)
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def name_must_be_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Name must contain only alphanumeric characters')
        return v
    
    @validator('horizon_days')
    def validate_horizon(cls, v):
        if v < 1 or v > 365:
            raise ValueError('Planning horizon must be between 1 and 365 days')
        return v
```

#### CORS Configuration

```python
# src/api/app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"]
)
```

### 9.4 Security Scanning

#### Automated Security Checks

```bash
# Security scanning in CI/CD pipeline
make security-check

# Bandit for Python security issues
bandit -r src/ -f json -o security-report.json

# Safety for known vulnerabilities
safety check --json --output safety-report.json

# SAST with semgrep
semgrep --config=auto src/
```

#### Secrets Management

```python
# src/security/secrets_manager.py
import boto3
from typing import Dict

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager')
    
    async def get_secret(self, secret_name: str) -> Dict[str, str]:
        """Retrieve secrets from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise
```

---

## 10. Performance & Optimization

### 10.1 Caching Strategy

#### Redis Caching Implementation

```python
# src/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Any, Optional
import pickle

class RedisCache:
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            data = await self.redis.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        try:
            ttl = ttl or self.default_ttl
            data = pickle.dumps(value)
            await self.redis.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate keys matching pattern"""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
```

#### Caching Decorator

```python
# src/utils/caching.py
from functools import wraps
import hashlib

def cache_result(ttl: int = 3600, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=1800, key_prefix="inventory")
async def get_inventory_summary(warehouse_id: str):
    # Expensive database query
    pass
```

### 10.2 Database Optimization

#### Query Optimization

```python
# Optimized queries with proper indexing
class InventoryRepository:
    async def get_low_stock_materials(self, warehouse_id: str) -> List[MaterialsInventory]:
        """Optimized query for low stock materials"""
        # Uses composite index on (warehouse_id, current_stock, safety_stock)
        query = select(MaterialsInventory).where(
            and_(
                MaterialsInventory.warehouse_id == warehouse_id,
                MaterialsInventory.current_stock <= MaterialsInventory.safety_stock,
                MaterialsInventory.is_active == True
            )
        ).order_by(
            (MaterialsInventory.current_stock / MaterialsInventory.safety_stock).asc()
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()
```

#### Connection Pooling

```python
# src/database/__init__.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,  # 20
    max_overflow=settings.database_max_overflow,  # 40
    pool_timeout=settings.database_pool_timeout,  # 30
    pool_recycle=settings.database_pool_recycle,  # 3600
    echo=settings.debug,
    future=True
)
```

#### Batch Operations

```python
# Efficient batch processing
async def batch_update_inventory(updates: List[InventoryUpdate]):
    """Update multiple inventory records efficiently"""
    async with AsyncSession(engine) as session:
        # Batch update using bulk operations
        for batch in chunk_list(updates, 1000):  # Process in chunks
            update_data = [
                {
                    "material_id": update.material_id,
                    "current_stock": update.new_stock,
                    "updated_at": datetime.utcnow()
                }
                for update in batch
            ]
            
            stmt = update(MaterialsInventory).where(
                MaterialsInventory.material_id == bindparam("material_id")
            ).values(
                current_stock=bindparam("current_stock"),
                updated_at=bindparam("updated_at")
            )
            
            await session.execute(stmt, update_data)
        
        await session.commit()
```

### 10.3 Asynchronous Processing

#### Background Tasks with Celery

```python
# src/core/tasks/ml_training.py
from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "efab_ai_enhanced",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['src.core.tasks']
)

@celery_app.task(bind=True, max_retries=3)
def train_ml_model(self, product_id: str, model_type: str):
    """Background ML model training"""
    try:
        # Model training logic
        model_trainer = MLModelTrainer()
        result = model_trainer.train(product_id, model_type)
        
        # Save model and update registry
        model_registry.save_model(result.model, product_id, model_type)
        
        return {
            "success": True,
            "model_id": result.model_id,
            "accuracy": result.accuracy
        }
        
    except Exception as exc:
        logger.error(f"Model training failed: {exc}")
        self.retry(countdown=60, exc=exc)
```

#### Async API Endpoints

```python
# Proper async endpoint implementation
@router.post("/planning/runs/{run_id}/execute")
async def execute_planning_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    planning_service: PlanningService = Depends()
):
    """Execute planning run asynchronously"""
    
    # Validate run exists and is ready
    planning_run = await planning_service.get_run(run_id)
    if not planning_run:
        raise HTTPException(404, "Planning run not found")
    
    # Start background execution
    background_tasks.add_task(
        planning_service.execute_run_async, 
        run_id
    )
    
    return {
        "message": "Planning run started",
        "run_id": run_id,
        "status": "running"
    }
```

### 10.4 Performance Monitoring

#### Application Metrics

```python
# src/utils/performance.py
import time
from functools import wraps
from prometheus_client import Histogram, Counter

# Performance metrics
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

database_query_duration = Histogram(
    'database_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

def monitor_performance(operation_type: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                database_query_duration.labels(
                    query_type=operation_type
                ).observe(duration)
        return wrapper
    return decorator
```

#### Performance Targets

| Metric | Target | Monitoring |
|--------|--------|------------|
| **API Response Time** | < 200ms (p95) | Prometheus + Grafana |
| **Planning Cycle** | < 2 minutes (1K materials) | Application logs |
| **ML Inference** | < 100ms | Model serving metrics |
| **Database Queries** | < 50ms (p95) | Query performance insights |
| **Cache Hit Rate** | > 85% | Redis metrics |
| **System Uptime** | > 99.9% | Health checks |

---

## 11. Testing Strategy

### 11.1 Test Architecture

The testing strategy follows a pyramid approach with comprehensive coverage across all layers:

```
    /\     E2E Tests (10%)
   /  \    - Full workflow testing
  /____\   - User journey validation
 /      \  
/________\  Integration Tests (20%)
          - API endpoint testing
          - Database integration
          - ERP connector testing
          
Unit Tests (70%)
- Business logic testing
- Model validation
- Utility function testing
```

### 11.2 Test Configuration

#### Pytest Setup

```python
# pytest.ini
[tool:pytest]
minversion = 7.0
addopts = -ra --strict-markers --cov=src --cov-branch --cov-report=term-missing:skip-covered --cov-fail-under=80
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    performance: marks tests as performance tests
    ml: marks tests as ML-related
```

#### Test Database Setup

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        app_env="testing",
        postgres_db="efab_ai_enhanced_test",
        redis_url="redis://localhost:6379/15",
        ml_model_path=Path("tests/fixtures/models"),
        enable_ml_recovery_mode=True
    )

@pytest_asyncio.fixture
async def async_db_session(test_async_engine):
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestAsyncSessionLocal = sessionmaker(
        bind=test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestAsyncSessionLocal() as session:
        yield session
    
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

### 11.3 Unit Testing

#### Business Logic Testing

```python
# tests/unit/engine/test_planning_engine.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.engine.planning.engine import PlanningEngine
from src.core.domain.planning import PlanningRun, PlanningRunStatus

class TestPlanningEngine:
    @pytest.fixture
    def planning_engine(self):
        return PlanningEngine()
    
    @pytest.fixture
    def sample_planning_run(self):
        return PlanningRun(
            id="test-run-1",
            name="Test Planning Run",
            status=PlanningRunStatus.CREATED,
            horizon_days=30
        )
    
    @pytest.mark.asyncio
    async def test_run_planning_success(self, planning_engine, sample_planning_run):
        # Arrange
        planning_engine._execute_phase = AsyncMock(return_value={"success": True})
        
        # Act
        result = await planning_engine.run_planning(sample_planning_run)
        
        # Assert
        assert result is not None
        assert sample_planning_run.status == PlanningRunStatus.COMPLETED
        assert planning_engine._execute_phase.call_count == 6  # All 6 phases
    
    @pytest.mark.asyncio
    async def test_planning_phase_failure(self, planning_engine, sample_planning_run):
        # Arrange
        planning_engine._execute_phase = AsyncMock(
            side_effect=Exception("Phase execution failed")
        )
        
        # Act & Assert
        with pytest.raises(Exception, match="Phase execution failed"):
            await planning_engine.run_planning(sample_planning_run)
        
        assert sample_planning_run.status == PlanningRunStatus.FAILED
```

#### ML Model Testing

```python
# tests/unit/ml/test_ensemble_model.py
import pytest
import numpy as np
import pandas as pd
from src.ml.models.ensemble_model import EnsembleModel

class TestEnsembleModel:
    @pytest.fixture
    def sample_data(self):
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        return pd.DataFrame({
            'date': dates,
            'value': np.random.randn(100).cumsum() + 100
        })
    
    @pytest.fixture
    def ensemble_model(self):
        return EnsembleModel(models=['prophet', 'arima', 'exponential_smoothing'])
    
    def test_model_initialization(self, ensemble_model):
        assert len(ensemble_model.models) == 3
        assert 'prophet' in ensemble_model.models
        assert ensemble_model.weights is None  # Not trained yet
    
    @pytest.mark.asyncio
    async def test_model_training(self, ensemble_model, sample_data):
        # Act
        await ensemble_model.fit(sample_data)
        
        # Assert
        assert ensemble_model.is_trained
        assert ensemble_model.weights is not None
        assert len(ensemble_model.weights) == 3
        assert abs(sum(ensemble_model.weights.values()) - 1.0) < 1e-6  # Weights sum to 1
    
    @pytest.mark.asyncio
    async def test_prediction(self, ensemble_model, sample_data):
        # Arrange
        await ensemble_model.fit(sample_data)
        
        # Act
        predictions = await ensemble_model.predict(steps=30)
        
        # Assert
        assert len(predictions) == 30
        assert all(pred > 0 for pred in predictions)  # Reasonable predictions
        assert ensemble_model.last_prediction_confidence > 0
```

### 11.4 Integration Testing

#### API Integration Tests

```python
# tests/integration/test_planning_api.py
import pytest
from httpx import AsyncClient
from src.api.app import app

@pytest.mark.asyncio
async def test_create_planning_run_integration():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Arrange
        payload = {
            "name": "Integration Test Run",
            "horizon_days": 30,
            "configuration": {
                "enable_ml_forecasting": True
            }
        }
        
        # Act
        response = await client.post(
            "/api/v1/planning/runs",
            json=payload,
            headers={"Authorization": "Bearer test-token"}
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Integration Test Run"
        assert data["status"] == "pending"
        assert "id" in data

@pytest.mark.asyncio
async def test_planning_run_execution_integration():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create planning run
        create_response = await client.post(
            "/api/v1/planning/runs",
            json={"name": "Test Run", "horizon_days": 7}
        )
        run_id = create_response.json()["id"]
        
        # Execute planning run
        execute_response = await client.post(
            f"/api/v1/planning/runs/{run_id}/execute"
        )
        
        assert execute_response.status_code == 202
        
        # Check status
        status_response = await client.get(
            f"/api/v1/planning/runs/{run_id}/status"
        )
        
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["overall_status"] in ["running", "completed"]
```

#### Database Integration Tests

```python
# tests/integration/test_inventory_repository.py
import pytest
from src.database.repositories.inventory import InventoryRepository
from src.database.models.inventory import MaterialsInventory

@pytest.mark.asyncio
async def test_inventory_repository_crud(async_db_session):
    # Arrange
    repo = InventoryRepository(async_db_session)
    material = MaterialsInventory(
        material_id="TEST001",
        material_name="Test Material",
        material_type="raw_material",
        current_stock=1000,
        safety_stock=200
    )
    
    # Act - Create
    created_material = await repo.create(material)
    assert created_material.id is not None
    
    # Act - Read
    retrieved_material = await repo.get_by_material_id("TEST001")
    assert retrieved_material.material_name == "Test Material"
    
    # Act - Update
    retrieved_material.current_stock = 800
    updated_material = await repo.update(retrieved_material)
    assert updated_material.current_stock == 800
    
    # Act - Delete
    await repo.delete(retrieved_material.id)
    deleted_material = await repo.get_by_id(retrieved_material.id)
    assert deleted_material is None
```

### 11.5 Performance Testing

#### Load Testing with k6

```javascript
// tests/performance/load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },   // Ramp up
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100
    { duration: '5m', target: 100 },  // Stay at 100
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'],  // 95% of requests under 200ms
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
  },
};

export default function() {
  // Test API health endpoint
  let health_response = http.get('http://localhost:8000/health');
  check(health_response, {
    'health status is 200': (r) => r.status === 200,
    'health response time < 100ms': (r) => r.timings.duration < 100,
  });
  
  // Test planning runs list
  let auth_headers = { 'Authorization': 'Bearer test-token' };
  let planning_response = http.get(
    'http://localhost:8000/api/v1/planning/runs',
    { headers: auth_headers }
  );
  check(planning_response, {
    'planning API status is 200': (r) => r.status === 200,
    'planning API response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);
}
```

#### ML Performance Testing

```python
# tests/performance/test_ml_performance.py
import pytest
import time
import numpy as np
from src.ml.models.ensemble_model import EnsembleModel

@pytest.mark.performance
class TestMLPerformance:
    @pytest.fixture
    def large_dataset(self):
        """Generate large dataset for performance testing"""
        size = 10000
        dates = pd.date_range('2020-01-01', periods=size, freq='D')
        values = np.random.randn(size).cumsum() + 1000
        return pd.DataFrame({'date': dates, 'value': values})
    
    @pytest.mark.asyncio
    async def test_training_performance(self, large_dataset):
        """Test model training performance with large dataset"""
        model = EnsembleModel()
        
        start_time = time.time()
        await model.fit(large_dataset)
        training_time = time.time() - start_time
        
        # Performance assertions
        assert training_time < 60  # Should complete within 1 minute
        assert model.is_trained
    
    @pytest.mark.asyncio
    async def test_prediction_performance(self, large_dataset):
        """Test prediction performance"""
        model = EnsembleModel()
        await model.fit(large_dataset)
        
        start_time = time.time()
        predictions = await model.predict(steps=365)  # 1 year forecast
        prediction_time = time.time() - start_time
        
        # Performance assertions
        assert prediction_time < 5  # Should complete within 5 seconds
        assert len(predictions) == 365
```

### 11.6 Test Execution

#### Running Tests

```bash
# All tests
make test

# Unit tests only
make test-unit

# Integration tests
make test-integration

# Performance tests
make test-performance

# ML-specific tests
pytest -m ml -v

# Coverage report
make test-cov

# Continuous testing
make test-watch
```

#### CI/CD Pipeline Testing

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: efab_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    
    - name: Run tests
      run: |
        poetry run pytest
      env:
        DATABASE_URL: postgresql://postgres:test_password@localhost/efab_test
        REDIS_URL: redis://localhost:6379/0
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 11.7 Test Quality Metrics

#### Coverage Requirements

- **Minimum Coverage**: 80% (enforced by pytest-cov)
- **Critical Paths**: 95% coverage required
- **New Code**: 100% coverage required

#### Test Performance Targets

| Test Type | Target Time | Actual Time |
|-----------|-------------|-------------|
| **Unit Tests** | < 2 minutes | ~1.5 minutes |
| **Integration Tests** | < 5 minutes | ~4 minutes |
| **Performance Tests** | < 10 minutes | ~8 minutes |
| **Full Test Suite** | < 15 minutes | ~12 minutes |

---

## 12. Troubleshooting

### 12.1 Common Issues

#### Database Connection Issues

**Problem**: Cannot connect to PostgreSQL database

**Symptoms**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solutions**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Start PostgreSQL if not running
make dev-db-start

# Check connection manually
psql -h localhost -U efab_user -d efab_ai_enhanced

# Reset database if corrupted
make db-reset
make db-upgrade
```

**Configuration Check**:
```python
# Verify database settings in .env
DATABASE_URL=postgresql://efab_user:efab_password@localhost:5432/efab_ai_enhanced

# Test connection programmatically
from src.database import engine
async with engine.begin() as conn:
    result = await conn.execute(text("SELECT 1"))
    print("Database connection successful")
```

#### Redis Connection Issues

**Problem**: Cannot connect to Redis for caching

**Symptoms**:
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solutions**:
```bash
# Check Redis status
docker-compose ps redis

# Start Redis
make dev-redis-start

# Test Redis connection
redis-cli ping
# Should return: PONG

# Clear Redis cache if needed
redis-cli FLUSHALL
```

#### ML Model Loading Failures

**Problem**: ML models fail to load or produce errors

**Symptoms**:
```
FileNotFoundError: No such file or directory: 'models/trained/prophet_model.pkl'
MLModelError: Model confidence below threshold
```

**Solutions**:
```bash
# Retrain models
make train-models

# Check model files exist
ls -la models/trained/

# Reset to simple models if ML fails
export ML_ENABLED=false
export USE_SIMPLE_MODELS_FALLBACK=true

# Verify model loading
python -c "from src.ml.models.ensemble_model import EnsembleModel; print('Models loaded successfully')"
```

#### ERP Integration Issues

**Problem**: ERP synchronization failures

**Symptoms**:
```
ERPConnectionError: Failed to authenticate with ERP system
HTTPTimeout: Request to ERP system timed out
```

**Solutions**:
```bash
# Check ERP connectivity
curl -I https://efab.bkiapps.com/api/health

# Verify API credentials
echo $ERP_API_KEY

# Test ERP connection
python -m src.data.connectors.erp_mcp_client --test-connection

# Fall back to CSV import
python -m src.data.validators.csv_validator --file data/imports/inventory.csv
```

### 12.2 Performance Issues

#### API Response Slowness

**Diagnosis**:
```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/v1/planning/runs"

# Monitor database queries
tail -f logs/app.log | grep "slow_query"

# Check Redis cache hit rate
redis-cli info stats | grep keyspace
```

**Solutions**:
```python
# Add caching to slow endpoints
@cache_result(ttl=1800, key_prefix="inventory")
async def get_inventory_summary():
    # Implementation

# Optimize database queries
query = select(MaterialsInventory).options(
    selectinload(MaterialsInventory.transactions)
).where(MaterialsInventory.warehouse_id == warehouse_id)

# Add database indexes
CREATE INDEX CONCURRENTLY idx_materials_warehouse_stock 
ON materials_inventory(warehouse_id, current_stock);
```

#### Memory Usage Issues

**Diagnosis**:
```bash
# Check memory usage
docker stats efab-api efab-worker

# Monitor Python memory usage
pip install memory-profiler
python -m memory_profiler src/api/app.py
```

**Solutions**:
```python
# Process data in chunks
async def process_large_dataset(data):
    chunk_size = 1000
    for chunk in chunk_list(data, chunk_size):
        await process_chunk(chunk)
        # Allow garbage collection
        gc.collect()

# Use generators instead of lists
def generate_inventory_items():
    for item in query_large_dataset():
        yield item

# Limit memory usage for ML models
model = EnsembleModel(max_memory_usage="2GB")
```

### 12.3 Error Patterns

#### Planning Engine Failures

**Error Pattern**: Phase execution timeouts
```python
# Increase timeout for complex planning runs
config = PlanningEngineConfig(
    phase_timeout_seconds=600,  # 10 minutes
    max_retries=5
)

# Monitor phase execution
logger.info(f"Phase {phase.name} started at {datetime.now()}")
```

**Error Pattern**: ML model convergence issues
```python
# Implement fallback strategies
class RobustForecaster:
    async def forecast(self, data):
        try:
            return await self.ml_forecast(data)
        except ConvergenceError:
            logger.warning("ML model failed, using statistical fallback")
            return await self.statistical_forecast(data)
        except Exception as e:
            logger.error(f"All forecasting methods failed: {e}")
            return self.simple_average_forecast(data)
```

#### Data Quality Issues

**Error Pattern**: Invalid ERP data
```python
# Implement data validation
class ERPDataValidator:
    def validate_inventory_data(self, data):
        errors = []
        
        for item in data:
            if item.current_stock < 0:
                errors.append(f"Negative stock for {item.material_id}")
                item.current_stock = 0  # Auto-fix
            
            if not item.material_name:
                errors.append(f"Missing name for {item.material_id}")
        
        if errors:
            logger.warning(f"Data quality issues found: {errors}")
        
        return data, errors
```

### 12.4 Debugging Tools

#### Application Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Or use IPython debugger
import ipdb; ipdb.set_trace()

# Async debugging
import aiomonitor
aiomonitor.start_monitor(loop=asyncio.get_event_loop())
```

#### Database Debugging

```sql
-- Check long-running queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Check database connections
SELECT 
    count(*) as connection_count,
    state 
FROM pg_stat_activity 
GROUP BY state;

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM materials_inventory 
WHERE warehouse_id = 'WH001' AND current_stock < safety_stock;
```

#### Production Monitoring

```bash
# View logs in real-time
docker-compose logs -f api

# Check system resources
docker exec efab-api top
docker exec efab-api df -h

# Monitor Redis
docker exec efab-redis redis-cli monitor

# Database monitoring
docker exec efab-postgres pg_stat_statements
```

### 12.5 Recovery Procedures

#### Database Recovery

```bash
# Restore from backup
gunzip latest_backup.sql.gz
psql -h localhost -U efab_user -d efab_ai_enhanced < latest_backup.sql

# Rebuild indexes if corrupted
docker exec efab-postgres psql -U efab_user -d efab_ai_enhanced -c "REINDEX DATABASE efab_ai_enhanced;"

# Reset to clean state
make db-reset
make db-upgrade
make db-seed
```

#### Service Recovery

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart api

# Rebuild and restart
docker-compose up -d --build --force-recreate api

# Check service health
curl http://localhost:8000/health
```

#### Data Recovery

```python
# Recover from ERP system
async def emergency_data_sync():
    """Emergency data synchronization from ERP"""
    erp_client = ERPClient()
    
    # Sync critical data
    inventory = await erp_client.get_all_inventory()
    await sync_inventory_data(inventory)
    
    suppliers = await erp_client.get_suppliers()
    await sync_supplier_data(suppliers)
    
    logger.info("Emergency data sync completed")

# Export data before recovery
async def export_current_data():
    """Export current data for backup"""
    data = {
        'inventory': await export_inventory(),
        'planning_runs': await export_planning_runs(),
        'forecasts': await export_forecasts()
    }
    
    with open(f'emergency_backup_{datetime.now().isoformat()}.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)
```

---

## 13. Technical Roadmap

### 13.1 Current Version (2.0.0) - Q4 2024

#### Completed Features ✅
- **Microservices Architecture**: FastAPI + Streamlit + PostgreSQL + Redis
- **6-Phase Planning Engine**: Complete supply chain optimization workflow
- **Multi-Model ML Ensemble**: Prophet, XGBoost, LightGBM, LSTM, ARIMA integration
- **ERP Integration**: Beverly Knits native connector with MCP protocol
- **Multi-Agent System**: Distributed agent architecture
- **Authentication & Authorization**: JWT-based security with RBAC
- **Docker Deployment**: Full containerization with docker-compose
- **Comprehensive Testing**: 80% test coverage with unit, integration, and performance tests

#### Known Technical Debt 🔧
- **Agent Communication**: Message bus needs optimization for high-throughput scenarios
- **ML Model Drift Detection**: Basic implementation needs enhancement
- **Database Connection Pooling**: Needs tuning for production scale
- **Async Exception Handling**: Some error paths need better async context management
- **API Rate Limiting**: Memory-based limiter needs Redis backend for scaling

### 13.2 Version 2.1.0 - Q1 2025

#### Enhanced Analytics & Intelligence 🎯

**Advanced ML Pipeline**
```python
# Planned implementation
class MLPipelineOrchestrator:
    """Next-generation ML pipeline with AutoML"""
    
    async def auto_model_selection(self, data_characteristics):
        """Intelligent model selection based on data patterns"""
        # AutoGluon integration for automated model selection
        # H2O.ai integration for advanced AutoML
        # Real-time A/B testing for model performance
        pass
    
    async def continuous_learning(self):
        """Implement online learning capabilities"""
        # Incremental model updates
        # Concept drift detection and adaptation
        # Active learning for data acquisition
        pass
```

**Real-Time Analytics Engine**
- Stream processing with Apache Kafka/Pulsar
- Real-time dashboard updates via WebSocket
- Live performance monitoring and alerting
- Predictive maintenance alerts

**Advanced Forecasting**
- Hierarchical forecasting for product families
- External factor integration (weather, economic indicators)
- Multi-horizon forecasting optimization
- Probabilistic forecasting with confidence intervals

#### Infrastructure Improvements 🚀

**Kubernetes-Native Deployment**
```yaml
# Planned Kubernetes architecture
apiVersion: v1
kind: Namespace
metadata:
  name: efab-production
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: efab-api-deployment
spec:
  replicas: 5
  strategy:
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  template:
    spec:
      containers:
      - name: api
        image: efab-ai-enhanced:2.1.0
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

**Enhanced Caching Strategy**
- Multi-level caching (L1: Memory, L2: Redis, L3: Database)
- Intelligent cache invalidation
- Cache warming strategies for critical data
- Distributed caching with Redis Cluster

### 13.3 Version 2.2.0 - Q2 2025

#### Edge Computing & Mobile 📱

**Edge Deployment**
```python
class EdgeModelServer:
    """Lightweight model serving for edge deployment"""
    
    def __init__(self):
        self.models = self._load_compressed_models()
        self.offline_capabilities = True
    
    async def predict_offline(self, input_data):
        """Predictions without internet connectivity"""
        # Quantized models for resource constraints
        # Federated learning synchronization
        pass
```

**Mobile Application**
- React Native app for supply chain managers
- Offline-capable inventory management
- Real-time notifications and alerts
- Barcode scanning integration

**IoT Integration**
- RFID/sensor data integration
- Real-time inventory tracking
- Environmental monitoring (temperature, humidity)
- Automated reorder triggers

#### Advanced Security 🔐

**Zero-Trust Architecture**
```python
class ZeroTrustManager:
    """Implement zero-trust security model"""
    
    async def verify_request(self, request_context):
        """Comprehensive request verification"""
        # Device fingerprinting
        # Behavioral analysis
        # Dynamic risk assessment
        # Micro-segmentation
        pass
```

**Enhanced Encryption**
- End-to-end encryption for sensitive data
- Homomorphic encryption for privacy-preserving ML
- Key rotation automation
- Hardware security module (HSM) integration

### 13.4 Version 3.0.0 - Q3 2025

#### AI-Native Architecture 🤖

**Large Language Model Integration**
```python
class SupplyChainLLM:
    """LLM-powered supply chain intelligence"""
    
    async def analyze_market_trends(self, query: str):
        """Natural language market analysis"""
        # GPT-4/Claude integration for insights
        # Retrieval-augmented generation (RAG)
        # Multi-modal analysis (text, images, charts)
        pass
    
    async def generate_optimization_strategies(self, context):
        """AI-generated optimization recommendations"""
        # Strategic planning assistance
        # Risk scenario generation
        # Automated report generation
        pass
```

**Computer Vision Integration**
- Automated quality inspection
- Warehouse layout optimization
- Defect detection in materials
- Inventory counting via drone/camera

**Autonomous Planning**
- Self-optimizing supply chain parameters
- Automatic supplier onboarding and evaluation
- Dynamic pricing optimization
- Autonomous contract negotiation

#### Global Scale Architecture 🌍

**Multi-Tenant SaaS Platform**
```python
class TenantManager:
    """Multi-tenant architecture for global deployment"""
    
    async def provision_tenant(self, tenant_config):
        """Dynamic tenant provisioning"""
        # Isolated data storage
        # Custom branding and configuration
        # Resource allocation and billing
        pass
```

**Regional Deployment**
- AWS/Azure/GCP multi-region deployment
- Data sovereignty compliance
- Localized currency and language support
- Regional supplier network integration

### 13.5 Version 3.1.0 - Q4 2025

#### Sustainability & ESG 🌱

**Carbon Footprint Tracking**
```python
class SustainabilityAnalyzer:
    """ESG metrics and carbon footprint analysis"""
    
    async def calculate_carbon_footprint(self, supply_chain_data):
        """Comprehensive carbon footprint calculation"""
        # Transportation emission tracking
        # Supplier sustainability scoring
        # Green alternative recommendations
        pass
    
    async def optimize_for_sustainability(self, constraints):
        """Multi-objective optimization including ESG factors"""
        # Cost vs. carbon tradeoff analysis
        # Sustainable supplier prioritization
        # Circular economy integration
        pass
```

**Circular Economy Features**
- Waste reduction optimization
- Recycling and upcycling tracking
- Sustainable material recommendations
- End-of-life product planning

#### Advanced Blockchain Integration ⛓️

**Supply Chain Transparency**
```python
class BlockchainTracker:
    """Blockchain-based supply chain transparency"""
    
    async def track_material_provenance(self, material_id):
        """Complete material journey tracking"""
        # Origin verification
        # Quality certification
        # Ethical sourcing validation
        pass
```

### 13.6 Performance & Scalability Targets

#### Version 2.1.0 Targets
| Metric | Current | Target |
|--------|---------|--------|
| **API Response Time** | 200ms (p95) | 100ms (p95) |
| **Planning Capacity** | 1K materials | 10K materials |
| **Concurrent Users** | 50 | 200 |
| **ML Inference** | 100ms | 50ms |
| **System Uptime** | 99.9% | 99.95% |

#### Version 3.0.0 Targets
| Metric | Target |
|--------|--------|
| **Global Scale** | 1M+ materials |
| **Multi-Tenant** | 1000+ organizations |
| **Real-Time Processing** | <10ms latency |
| **AI Response Time** | <5s for complex queries |
| **System Uptime** | 99.99% |

### 13.7 Technology Evolution

#### Current Stack Evolution
```mermaid
graph LR
    A[FastAPI 0.104] --> B[FastAPI 0.110+]
    C[Python 3.11] --> D[Python 3.12+]
    E[PostgreSQL 16] --> F[PostgreSQL 17+]
    G[Redis 7] --> H[Redis 8/KeyDB]
    I[Docker] --> J[Kubernetes]
    K[Streamlit] --> L[Next.js/React]
```

#### Emerging Technologies Integration
- **Quantum Computing**: For complex optimization problems
- **5G/6G Networks**: Ultra-low latency communication
- **Digital Twins**: Virtual supply chain modeling
- **Extended Reality (XR)**: Immersive data visualization
- **Neuromorphic Computing**: Energy-efficient AI processing

### 13.8 Migration Strategy

#### Database Migration Path
```sql
-- Version 2.1.0 Schema Changes
ALTER TABLE materials_inventory ADD COLUMN carbon_footprint DECIMAL(10,3);
ALTER TABLE suppliers ADD COLUMN sustainability_score DECIMAL(3,2);
CREATE TABLE ml_model_experiments (
    id UUID PRIMARY KEY,
    model_name VARCHAR(100),
    experiment_config JSONB,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### API Versioning Strategy
```python
# Backward compatibility maintenance
@router.get("/api/v2/planning/runs", tags=["planning-v2"])
async def create_planning_run_v2(request: PlanningRunRequestV2):
    """Enhanced planning run with AI-powered insights"""
    pass

@router.get("/api/v1/planning/runs", tags=["planning-v1"], deprecated=True)
async def create_planning_run_v1(request: PlanningRunRequestV1):
    """Legacy planning run endpoint (deprecated)"""
    # Convert v1 request to v2 format
    v2_request = convert_v1_to_v2(request)
    return await create_planning_run_v2(v2_request)
```

### 13.9 Open Source Strategy

#### Community Contributions
- **Core Framework**: Open source the base planning engine
- **ML Models**: Community-driven model contributions
- **Connectors**: Open ERP connector framework
- **Documentation**: Community-maintained documentation

#### Enterprise vs Open Source
```python
# Open Source Core
class OpenSourcePlanningEngine:
    """Basic planning engine available to community"""
    pass

# Enterprise Extensions
class EnterprisePlanningEngine(OpenSourcePlanningEngine):
    """Enhanced features for enterprise customers"""
    
    def __init__(self):
        super().__init__()
        self.advanced_ml_models = EnterpriseMLSuite()
        self.premium_connectors = PremiumERPConnectors()
        self.24x7_support = EnterpriseSupportPortal()
```

This roadmap ensures continuous evolution while maintaining backward compatibility and providing clear migration paths for existing deployments. The focus remains on delivering tangible business value while adopting cutting-edge technologies responsibly.

---

## Conclusion

The eFab AI Enhanced platform represents a significant advancement in supply chain optimization technology for textile manufacturing. With its microservices architecture, intelligent ML forecasting, and comprehensive planning engine, it provides a robust foundation for modern supply chain management.

This documentation serves as the definitive reference for developers, operators, and stakeholders working with the platform. Regular updates to this documentation ensure it remains current with the evolving codebase and feature set.

For additional support or questions, please refer to the project repository or contact the development team.

---

**Document Version**: 1.0.0
**Last Updated**: January 2025
**Next Review**: March 2025

# System Overview

## Executive Summary

EFAB AI Supply Chain Planner is an enterprise-grade supply chain optimization platform specifically designed for textile manufacturing. It combines a production-ready 6-phase planning engine with modern ML capabilities, real-time ERP integration via MCP (Model Context Protocol), and a robust fallback system ensuring 100% uptime.

## Business Context

### Problem Statement
Textile manufacturers face complex supply chain challenges:
- Multi-level BOMs with 100+ components per product
- Long lead times (60-180 days) for raw materials
- Volatile demand patterns with seasonal variations
- Multiple suppliers with varying reliability
- High inventory carrying costs
- Manual planning taking days to complete

### Solution
EFAB AI provides:
- Automated 6-phase planning completing in <2 minutes
- 15-25% reduction in inventory costs
- 5-10% procurement savings through optimization
- Real-time visibility into supply chain status
- ML-powered forecasting with guaranteed fallback
- Seamless ERP integration

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Interface Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │  Streamlit  │  │   React SPA  │  │ Mobile (PWA) │  │   API   │ │
│  │     UI      │  │   (Future)   │  │   (Future)   │  │  Docs   │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └────┬────┘ │
└─────────┼─────────────────┼──────────────────┼──────────────┼──────┘
          │                 │                  │              │
┌─────────▼─────────────────▼──────────────────▼──────────────▼──────┐
│                            API Gateway                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │   FastAPI   │  │  WebSocket   │  │    GraphQL   │  │  Auth   │ │
│  │  REST API   │  │   Server     │  │   (Future)   │  │   JWT   │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └────┬────┘ │
└─────────┼─────────────────┼──────────────────┼──────────────┼──────┘
          │                 │                  │              │
┌─────────▼─────────────────▼──────────────────▼──────────────▼──────┐
│                      Business Logic Layer                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │  Planning   │  │   Domain     │  │   ML/AI      │  │  Data   │ │
│  │   Engine    │  │   Services   │  │   Engine     │  │ Quality │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └────┬────┘ │
└─────────┼─────────────────┼──────────────────┼──────────────┼──────┘
          │                 │                  │              │
┌─────────▼─────────────────▼──────────────────▼──────────────▼──────┐
│                        Data Access Layer                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │ PostgreSQL  │  │    Redis     │  │  MCP Client  │  │   S3    │ │
│  │  Database   │  │    Cache     │  │     (ERP)    │  │ Storage │ │
│  └─────────────┘  └──────────────┘  └──────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. Planning Engine (Core Business Logic)
The heart of the system, implementing a 6-phase optimization cycle:

```python
# Simplified Planning Flow
async def execute_planning_cycle(request: PlanningRequest) -> PlanningResult:
    # Phase 1: Unify forecasts from multiple sources
    forecasts = await unify_forecasts(request.horizon_days)
    
    # Phase 2: Explode multi-level BOMs
    material_requirements = await explode_boms(forecasts)
    
    # Phase 3: Net against current inventory
    net_requirements = await calculate_net_requirements(
        material_requirements, 
        current_inventory
    )
    
    # Phase 4: Optimize procurement (EOQ)
    optimized_orders = await optimize_procurement(net_requirements)
    
    # Phase 5: Select suppliers based on performance
    supplier_allocation = await allocate_to_suppliers(optimized_orders)
    
    # Phase 6: Generate outputs
    return generate_planning_outputs(supplier_allocation)
```

#### 2. ML/AI Engine with Fallback
Ensures predictions always work:

```
┌─────────────────┐
│ Forecast Request│
└────────┬────────┘
         │
    ┌────▼────┐     ┌─────────────┐
    │   ML    │────▶│ Confidence  │
    │ Models  │     │   Check     │
    └─────────┘     └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Confidence  │───No──┐
                    │   > 0.8?    │       │
                    └──────┬──────┘       │
                           │Yes           │
                    ┌──────▼──────┐  ┌────▼────┐
                    │  Use ML     │  │Fallback │
                    │  Forecast   │  │ Simple  │
                    └─────────────┘  └─────────┘
```

#### 3. Data Integration via MCP
Real-time ERP synchronization:

```
ERP Systems          MCP Protocol         Application
┌──────────┐       ┌────────────┐      ┌─────────────┐
│   SAP    │◀─────▶│            │      │             │
├──────────┤       │    MCP     │◀────▶│ MCP Client  │
│  Oracle  │◀─────▶│   Server   │      │             │
├──────────┤       │            │      └──────┬──────┘
│ Dynamics │◀─────▶│            │             │
└──────────┘       └────────────┘      ┌──────▼──────┐
                                       │ Data Pipeline│
                                       └─────────────┘
```

## Domain Model

### Core Entities

#### Material
Represents any material in the supply chain:
```python
class Material:
    id: MaterialId
    name: str
    category: MaterialCategory
    unit_of_measure: UnitOfMeasure
    specifications: Dict[str, Any]
    lead_time_days: int
    minimum_order_quantity: float
    active: bool
```

#### Supplier
Represents material suppliers:
```python
class Supplier:
    id: SupplierId
    name: str
    performance_score: float  # 0.0 to 1.0
    materials: List[MaterialId]
    lead_times: Dict[MaterialId, int]
    capacity_constraints: Dict[MaterialId, float]
    payment_terms: PaymentTerms
```

#### BOM (Bill of Materials)
Defines product composition:
```python
class BOM:
    parent_material: MaterialId
    components: List[BOMComponent]
    effective_date: date
    expiry_date: Optional[date]
    
class BOMComponent:
    material: MaterialId
    quantity: float
    unit_of_measure: UnitOfMeasure
    waste_percentage: float
```

#### PlanningRun
Tracks planning execution:
```python
class PlanningRun:
    id: UUID
    status: PlanningStatus
    parameters: PlanningParameters
    started_at: datetime
    completed_at: Optional[datetime]
    results: Optional[PlanningResults]
    metrics: PlanningMetrics
```

## Data Flow

### 1. Input Data Flow
```
CSV Files ─────┐
               ├───▶ Data Validator ───▶ Quality Fixer ───▶ Database
MCP Stream ────┘                              │
                                             ▼
                                     Planning Engine
```

### 2. Planning Execution Flow
```
User Request ───▶ API ───▶ Planning Queue ───▶ Planning Engine
                    │                               │
                    ▼                               ▼
              WebSocket ◀──── Progress ────── Status Updates
                    │                               │
                    ▼                               ▼
                Client ◀───── Results ──────── Completed
```

### 3. ML Prediction Flow
```
Historical Data ───▶ Feature Engineering ───▶ Model Selection
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │ Confidence  │
                                            │ Evaluation  │
                                            └──────┬──────┘
                                                   │
                        ┌──────────────────────────┼───────────────────┐
                        ▼                          ▼                   ▼
                   High Conf.                 Medium Conf.         Low Conf.
                   Use LSTM                   Use Ensemble      Use Simple MA
```

## Security Architecture

### Authentication & Authorization
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│     API      │────▶│    Auth     │
│             │     │   Gateway    │     │   Service   │
└─────────────┘     └──────────────┘     └──────┬──────┘
      ▲                                          │
      │                                          ▼
      │                                   ┌─────────────┐
      └───────── JWT Token ──────────────│   Database  │
                                         └─────────────┘
```

### Data Security
- **Encryption at Rest**: AES-256 for database
- **Encryption in Transit**: TLS 1.3 for all connections
- **Data Masking**: PII automatically masked in logs
- **Audit Trail**: All data access logged

## Performance Characteristics

### Scalability Metrics
- **Materials**: Tested up to 10,000 materials
- **Suppliers**: Handles 500+ suppliers
- **BOMs**: Processes 5-level deep BOMs
- **Users**: Supports 100+ concurrent users
- **Planning Cycles**: <2 minutes for typical scenarios

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB for application + data growth
- **Network**: 10Mbps for MCP streaming

## Deployment Architecture

### Production Deployment
```
┌─────────────────────────────────────────────┐
│             Load Balancer (ALB)             │
└──────────────────┬─────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│  App    │  │  App    │  │  App    │
│ Server  │  │ Server  │  │ Server  │
│   #1    │  │   #2    │  │   #3    │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  ▼
         ┌────────────────┐
         │   PostgreSQL   │
         │   (Primary)    │
         └───────┬────────┘
                 │
         ┌───────┴────────┐
         ▼                ▼
  ┌────────────┐  ┌────────────┐
  │  Read      │  │  Read      │
  │ Replica #1 │  │ Replica #2 │
  └────────────┘  └────────────┘
```

### Container Architecture
```yaml
services:
  app:
    image: efab-ai:latest
    replicas: 3
    resources:
      limits:
        cpu: "2"
        memory: "4Gi"
    
  worker:
    image: efab-ai-worker:latest
    replicas: 2
    resources:
      limits:
        cpu: "4"
        memory: "8Gi"
    
  redis:
    image: redis:7-alpine
    replicas: 1
    
  postgres:
    image: postgres:16
    replicas: 1
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

## Monitoring & Observability

### Metrics Collection
```
Application ──┐
              ├──▶ Prometheus ──▶ Grafana
System ───────┘         │
                       ▼
                  AlertManager ──▶ PagerDuty/Slack
```

### Key Metrics
- **Business Metrics**:
  - Planning cycles per day
  - Average cycle duration
  - Forecast accuracy
  - Cost savings achieved

- **System Metrics**:
  - API response time (p50, p95, p99)
  - Database query performance
  - Cache hit ratio
  - Error rates

- **ML Metrics**:
  - Model confidence scores
  - Fallback usage rate
  - Prediction accuracy
  - Training frequency

## Integration Points

### 1. ERP Systems
- **SAP**: Via MCP protocol
- **Oracle NetSuite**: Via MCP protocol
- **Microsoft Dynamics**: Via MCP protocol
- **Custom ERPs**: Via REST API adapter

### 2. External Services
- **Email**: SMTP for notifications
- **SMS**: Twilio for alerts
- **Cloud Storage**: S3-compatible for backups
- **Analytics**: Export to data warehouse

### 3. Future Integrations
- **IoT Sensors**: Real-time inventory tracking
- **Blockchain**: Supply chain transparency
- **AI Assistants**: Natural language queries
- **Mobile Apps**: iOS/Android native apps

## Disaster Recovery

### Backup Strategy
- **Database**: Daily full backup, hourly incremental
- **Files**: Real-time sync to S3
- **Configuration**: Version controlled in Git

### Recovery Objectives
- **RPO** (Recovery Point Objective): 1 hour
- **RTO** (Recovery Time Objective): 4 hours
- **Backup Retention**: 30 days
- **Geographic Redundancy**: Multi-region backups

## Development Workflow

### Git Flow
```
main ────────────────────────────────────────
  │                                    │
  └─▶ develop ────────────────────────┴────
       │     │                         │
       └─▶ feature/planning-v2 ────────┘
       │                               
       └─▶ hotfix/security-patch ──────────▶ main
```

### CI/CD Pipeline
```
Code Push ──▶ Lint ──▶ Test ──▶ Build ──▶ Security Scan ──▶ Deploy
                │        │                      │
                ▼        ▼                      ▼
             Format   Coverage              Vulnerability
             Check    Report                  Report
```

## Future Roadmap

### Phase 1 (Current)
- ✅ Core planning engine
- ✅ ML fallback system
- ✅ Basic UI
- 🚧 MCP integration
- 🚧 API development

### Phase 2 (Q2 2025)
- 📋 Advanced ML models
- 📋 Real-time collaboration
- 📋 Mobile app
- 📋 Advanced analytics

### Phase 3 (Q3 2025)
- 📋 IoT integration
- 📋 Blockchain tracking
- 📋 AI assistant
- 📋 Predictive maintenance

## Conclusion

EFAB AI Supply Chain Planner represents a modern approach to supply chain optimization, combining proven business logic with cutting-edge technology. The system's architecture ensures reliability, scalability, and maintainability while delivering significant business value through automation and optimization.