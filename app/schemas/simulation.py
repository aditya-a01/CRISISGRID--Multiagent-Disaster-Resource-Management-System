"""Pydantic schemas for simulation data"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SimulationStateSchema(BaseModel):
    """Current state of a simulation"""

    id: int
    name: str
    current_timestep: int
    total_timesteps: int
    is_running: bool
    is_completed: bool
    power_available: float
    water_available: float
    stability_score: float
    unmet_demand: float
    risk_level: float

    class Config:
        from_attributes = True


class SimulationSchema(SimulationStateSchema):
    """Complete simulation schema"""

    description: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SimulationCreateSchema(BaseModel):
    """Schema for creating a new simulation"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    total_timesteps: int = Field(default=100, ge=1)
