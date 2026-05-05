"""Pydantic schemas for agent data"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class AgentType(str, Enum):
    HOSPITAL = "hospital"
    WATER = "water"
    POWER = "power"
    EMERGENCY = "emergency"


class BehaviorProfile(str, Enum):
    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    ADAPTIVE = "adaptive"


class AgentStateSchema(BaseModel):
    """State snapshot of an agent at a timestep"""

    id: int
    name: str
    agent_type: AgentType
    current_demand: float
    allocated_resources: float
    current_bid: float
    unmet_demand: float
    trust_score: float = Field(..., ge=0.0, le=1.0)
    priority_level: float
    risk_tolerance: float = Field(..., ge=0.0, le=1.0)
    cooperation_level: float = Field(..., ge=0.0, le=1.0)

    class Config:
        from_attributes = True


class AgentSchema(AgentStateSchema):
    """Complete agent schema including metadata"""

    simulation_id: int
    behavior_profile: BehaviorProfile
    dependency_factor: float
    urgency_bias: float
    max_demand: float
    min_demand: float
    memory_log: List[dict] = []

    class Config:
        from_attributes = True
