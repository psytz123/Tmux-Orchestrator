"""
Inventory related database models
"""
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import enum
import uuid

from src.database.connection import Base


class MaterialType(enum.Enum):
    """Material type enumeration"""
    RAW_MATERIAL = "raw_material"
    FABRIC = "fabric"
    TRIM = "trim"
    ACCESSORY = "accessory"
    PACKAGING = "packaging"
    CONSUMABLE = "consumable"


class MaterialsInventory(Base):
    """Materials inventory model"""
    __tablename__ = "materials_inventory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id = Column(String(100), unique=True, nullable=False, index=True)
    material_name = Column(String(255), nullable=False)
    material_type = Column(Enum(MaterialType), nullable=False)
    sku = Column(String(100), unique=True)
    category = Column(String(100), index=True)
    
    # Stock levels
    current_stock = Column(Numeric(15, 3), nullable=False, default=0)
    reserved_stock = Column(Numeric(15, 3), nullable=False, default=0)
    available_stock = Column(Numeric(15, 3), nullable=False, default=0)
    safety_stock = Column(Numeric(15, 3), nullable=False, default=0)
    
    # Reorder parameters
    reorder_point = Column(Numeric(15, 3), nullable=False, default=0)
    reorder_quantity = Column(Numeric(15, 3), nullable=False, default=0)
    
    # Unit information
    unit_of_measure = Column(String(20), nullable=False, default="EA")
    unit_cost = Column(Numeric(15, 3))
    
    # Lead time
    lead_time_days = Column(Integer, nullable=False, default=7)
    
    # Location
    warehouse_id = Column(String(50), index=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('current_stock >= 0', name='check_current_stock_positive'),
        CheckConstraint('reserved_stock >= 0', name='check_reserved_stock_positive'),
        CheckConstraint('available_stock >= 0', name='check_available_stock_positive'),
    )
    
    def __repr__(self):
        return f"<MaterialsInventory(material_id={self.material_id}, name={self.material_name})>"
    
    def calculate_available_stock(self):
        """Calculate available stock"""
        self.available_stock = max(0, self.current_stock - self.reserved_stock)
        return self.available_stock
    
    def needs_reorder(self) -> bool:
        """Check if material needs reordering"""
        return self.available_stock <= self.reorder_point
    
    def get_reorder_quantity(self) -> float:
        """Get quantity to reorder"""
        if self.needs_reorder():
            return max(self.reorder_quantity, self.safety_stock - self.available_stock)
        return 0