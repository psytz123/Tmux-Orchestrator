"""
Core configuration management for eFab AI Enhanced
"""
from typing import List, Dict, Any, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import json


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    app_name: str = Field(default="eFab-AI-Enhanced")
    app_version: str = Field(default="2.0.0")
    env: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    cors_origins: List[str] = Field(default=["http://localhost:8501"])
    
    # UI
    ui_host: str = Field(default="0.0.0.0")
    ui_port: int = Field(default=8501)
    
    # Database
    database_url: str = Field(
        default="postgresql://efab_user:efab_password@localhost:5432/efab_db"
    )
    db_echo: bool = Field(default=False)
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_password: Optional[str] = Field(default=None)
    redis_db: int = Field(default=0)
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1")
    celery_result_backend: str = Field(default="redis://localhost:6379/2")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-this")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)
    
    # ERP Integration
    beverly_knits_api_url: Optional[str] = Field(default=None)
    beverly_knits_api_key: Optional[str] = Field(default=None)
    sap_endpoint: Optional[str] = Field(default=None)
    sap_client_id: Optional[str] = Field(default=None)
    sap_client_secret: Optional[str] = Field(default=None)
    
    # ML Configuration
    ml_model_path: str = Field(default="./models")
    ml_confidence_threshold: float = Field(default=0.8)
    ml_ensemble_weights: Dict[str, float] = Field(
        default={
            "prophet": 0.3,
            "xgboost": 0.3,
            "lightgbm": 0.2,
            "lstm": 0.2
        }
    )
    
    # Planning Engine
    planning_horizon_days: int = Field(default=30)
    optimization_algorithm: str = Field(default="mixed_integer")
    objective_function: str = Field(default="minimize_cost")
    max_iterations: int = Field(default=1000)
    convergence_tolerance: float = Field(default=0.001)
    
    # Monitoring
    enable_metrics: bool = Field(default=True)
    metrics_port: int = Field(default=9090)
    enable_tracing: bool = Field(default=False)
    jaeger_agent_host: str = Field(default="localhost")
    jaeger_agent_port: int = Field(default=6831)
    
    # Feature Flags
    enable_ml_forecasting: bool = Field(default=True)
    enable_multi_agent: bool = Field(default=True)
    enable_real_time_updates: bool = Field(default=True)
    enable_advanced_analytics: bool = Field(default=True)
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    @validator("ml_ensemble_weights", pre=True)
    def parse_ml_weights(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @property
    def is_production(self) -> bool:
        return self.env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.env == "development"
    
    @property
    def database_url_async(self) -> str:
        """Convert sync database URL to async"""
        if self.database_url.startswith("sqlite"):
            return self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()