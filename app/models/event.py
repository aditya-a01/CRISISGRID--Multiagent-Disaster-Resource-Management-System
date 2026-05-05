"""Event model - represents disaster events in simulations"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum, Index, CheckConstraint
from app.models.base import Base
import enum


class EventType(str, enum.Enum):
    """Types of disaster events"""

    POWER_OUTAGE = "power_outage"
    WATER_SHORTAGE = "water_shortage"
    DEMAND_SPIKE = "demand_spike"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    RECOVERY = "recovery"


class Event(Base):
    """Database model for simulation events"""

    __tablename__ = "events"
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_event_sim_timestep', 'simulation_id', 'timestep'),
        Index('idx_event_type', 'event_type'),
        CheckConstraint('severity >= 0.0 AND severity <= 1.0', name='ck_severity_range'),
    )

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    timestep = Column(Integer, nullable=False)

    event_type = Column(SQLEnum(EventType), nullable=False)
    severity = Column(Float, nullable=False)  # 0.0 to 1.0
    affected_agent_type = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<Event type={self.event_type} severity={self.severity} step={self.timestep}>"
