"""Pydantic schemas for allocation data"""

from pydantic import BaseModel, Field
from typing import Optional


class AllocationSchema(BaseModel):
    """Resource allocation schema"""

    id: int
    simulation_id: int
    agent_id: int
    timestep: int
    resource_type: str
    allocated_amount: float
    requested_amount: float
    utility_score: float
    was_fulfilled: float = Field(..., ge=0.0, le=1.0)
    explanation: Optional[str] = None

    class Config:
        from_attributes = True
