"""
Planning related database models
"""
from sqlalchemy import Column, String, Text, Numeric, Integer, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from src.database.connection import Base


class PlanningStatus(enum.Enum):
    """Planning run status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationAlgorithm(enum.Enum):
    """Optimization algorithm types"""
    MIXED_INTEGER = "mixed_integer"
    LINEAR_PROGRAMMING = "linear_programming"
    GENETIC_ALGORITHM = "genetic_algorithm"
    SIMULATED_ANNEALING = "simulated_annealing"
    CONSTRAINT_PROGRAMMING = "constraint_programming"


class PlanningRun(Base):
    """Planning run model"""
    __tablename__ = "planning_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(PlanningStatus), nullable=False, default=PlanningStatus.PENDING)
    
    # Planning parameters
    planning_horizon_days = Column(Integer, nullable=False, default=30)
    optimization_algorithm = Column(String(100), nullable=False, default="mixed_integer")
    objective_function = Column(String(100), nullable=False, default="minimize_cost")
    
    # Execution details
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_time_seconds = Column(Numeric(10, 3))
    
    # Results
    total_cost = Column(Numeric(15, 2))
    total_units_planned = Column(Integer)
    optimization_score = Column(Numeric(5, 2))
    
    # Metadata
    parameters = Column(JSON)
    results = Column(JSON)
    error_message = Column(Text)
    
    # User tracking
    created_by = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    phases = relationship("PlanningPhase", back_populates="planning_run", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PlanningRun(id={self.id}, name={self.name}, status={self.status})>"


class PlanningPhase(Base):
    """Planning phase execution model"""
    __tablename__ = "planning_phases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_run_id = Column(UUID(as_uuid=True), ForeignKey("planning_runs.id"), nullable=False)
    phase_number = Column(Integer, nullable=False)
    phase_name = Column(String(100), nullable=False)
    status = Column(Enum(PlanningStatus), nullable=False, default=PlanningStatus.PENDING)
    
    # Execution details
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    execution_time_seconds = Column(Numeric(10, 3))
    
    # Phase-specific data
    input_data = Column(JSON)
    output_data = Column(JSON)
    metrics = Column(JSON)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    planning_run = relationship("PlanningRun", back_populates="phases")
    
    def __repr__(self):
        return f"<PlanningPhase(phase={self.phase_number}, name={self.phase_name}, status={self.status})>"