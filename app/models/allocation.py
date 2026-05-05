"""Allocation model - represents resource allocations to agents"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Index, CheckConstraint
from datetime import datetime
from app.models.base import Base


class Allocation(Base):
    """Database model for resource allocations"""

    __tablename__ = "allocations"
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_allocation_sim_timestep', 'simulation_id', 'timestep'),
        Index('idx_allocation_agent_resource', 'agent_id', 'resource_type'),
        Index('idx_allocation_resource_type', 'resource_type'),
        CheckConstraint('was_fulfilled >= 0.0 AND was_fulfilled <= 1.0', name='ck_fulfilled_range'),
        CheckConstraint('allocated_amount >= 0.0', name='ck_allocated_positive'),
        CheckConstraint('requested_amount >= 0.0', name='ck_requested_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    timestep = Column(Integer, nullable=False)

    # Allocation details
    resource_type = Column(String(50), nullable=False)  # 'power' or 'water'
    allocated_amount = Column(Float, nullable=False)
    requested_amount = Column(Float, nullable=False)
    utility_score = Column(Float, nullable=False)

    # Metadata
    was_fulfilled = Column(Float, default=0.0, nullable=False)  # Percentage fulfilled
    explanation = Column(String(1000), nullable=True)

    def __repr__(self):
        return f"<Allocation agent={self.agent_id} resource={self.resource_type} amount={self.allocated_amount} step={self.timestep}>"
