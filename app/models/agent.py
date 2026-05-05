"""Agent model - represents autonomous crisis response agents"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, Enum as SQLEnum, Index, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum


class AgentType(str, enum.Enum):
    """Types of agents in the crisis response system"""

    HOSPITAL = "hospital"
    WATER = "water"
    POWER = "power"
    EMERGENCY = "emergency"


class BehaviorProfile(str, enum.Enum):
    """Behavior profiles for agents"""

    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    ADAPTIVE = "adaptive"


class Agent(Base):
    """Database model for autonomous crisis response agents"""

    __tablename__ = "agents"
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_agent_simulation_id', 'simulation_id'),
        Index('idx_agent_trust_score', 'trust_score'),
        Index('idx_agent_sim_type', 'simulation_id', 'agent_type'),
        CheckConstraint('trust_score >= 0.0 AND trust_score <= 1.0', name='ck_trust_range'),
        CheckConstraint('priority_level >= 0.5', name='ck_priority_positive'),
        CheckConstraint('risk_tolerance >= 0.0 AND risk_tolerance <= 1.0', name='ck_risk_tolerance_range'),
        CheckConstraint('cooperation_level >= 0.0 AND cooperation_level <= 1.0', name='ck_cooperation_range'),
        CheckConstraint('urgency_bias >= 0.0 AND urgency_bias <= 1.0', name='ck_urgency_range'),
    )

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    agent_type = Column(SQLEnum(AgentType), nullable=False)
    name = Column(String(255), nullable=False)

    # Demand and allocation
    current_demand = Column(Float, nullable=False)
    allocated_resources = Column(Float, default=0.0, nullable=False)
    max_demand = Column(Float, nullable=False)
    min_demand = Column(Float, nullable=False)

    # Priority and dependency
    priority_level = Column(Float, default=1.0, nullable=False)
    dependency_factor = Column(Float, default=1.0, nullable=False)

    # Behavioral characteristics
    behavior_profile = Column(SQLEnum(BehaviorProfile), default=BehaviorProfile.ADAPTIVE, nullable=False)
    risk_tolerance = Column(Float, default=0.5, nullable=False)  # 0.0 (risk-averse) to 1.0 (risk-seeking)
    cooperation_level = Column(Float, default=0.5, nullable=False)  # 0.0 (competitive) to 1.0 (cooperative)
    urgency_bias = Column(Float, default=0.5, nullable=False)  # 0.0 (patient) to 1.0 (urgent)

    # Trust and memory
    trust_score = Column(Float, default=0.5, nullable=False)  # 0.0 to 1.0
    memory_log = Column(JSON, default=list, nullable=False)  # List of past interactions

    # State
    current_bid = Column(Float, default=0.0, nullable=False)
    unmet_demand = Column(Float, default=0.0, nullable=False)

    def __repr__(self):
        return f"<Agent id={self.id} type={self.agent_type} name={self.name} demand={self.current_demand}>"
