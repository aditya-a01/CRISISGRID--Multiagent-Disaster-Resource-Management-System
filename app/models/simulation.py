"""Simulation model - represents a crisis response simulation instance"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index, CheckConstraint
from datetime import datetime
from app.models.base import Base


class Simulation(Base):
    """Database model for crisis response simulations"""

    __tablename__ = "simulations"
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_simulation_created_at', 'created_at'),
        Index('idx_simulation_is_completed', 'is_completed'),
        CheckConstraint('stability_score >= 0.0 AND stability_score <= 1.0', name='ck_stability_range'),
        CheckConstraint('risk_level >= 0.0 AND risk_level <= 1.0', name='ck_risk_range'),
        CheckConstraint('unmet_demand >= 0.0', name='ck_unmet_positive'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # Simulation state
    current_timestep = Column(Integer, default=0, nullable=False)
    total_timesteps = Column(Integer, nullable=False)
    is_running = Column(Boolean, default=False, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    # Resource state
    power_available = Column(Float, nullable=False)
    water_available = Column(Float, nullable=False)

    # Metrics
    stability_score = Column(Float, default=1.0, nullable=False)
    unmet_demand = Column(Float, default=0.0, nullable=False)
    risk_level = Column(Float, default=0.0, nullable=False)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Simulation id={self.id} name={self.name} step={self.current_timestep}>"
