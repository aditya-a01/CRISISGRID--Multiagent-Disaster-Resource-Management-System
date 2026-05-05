"""Response schemas for API endpoints"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.agent import AgentStateSchema
from app.schemas.allocation import AllocationSchema


class MetricsSchema(BaseModel):
    """System metrics at a timestep"""

    stability_score: float = Field(..., ge=0.0, le=1.0, description="Overall system stability (0=unstable, 1=stable)")
    unmet_demand: float = Field(..., ge=0.0, description="Total unmet resource demand")
    risk_level: float = Field(..., ge=0.0, le=1.0, description="System risk level (0=safe, 1=critical)")


class SimulationStepResponse(BaseModel):
    """Response from a single simulation timestep"""

    state: Dict[str, Any]  # Simulation state snapshot
    agents: List[AgentStateSchema]  # All agents' state
    allocations: List[AllocationSchema]  # Resource allocations for this step
    bids: List[Dict[str, Any]]  # Agent bids submitted
    metrics: MetricsSchema  # System metrics
    explanations: List[str] = []  # Human-readable explanations of decisions

    class Config:
        json_schema_extra = {
            "example": {
                "state": {
                    "simulation_id": 1,
                    "current_timestep": 5,
                    "power_available": 950.0,
                    "water_available": 480.0,
                },
                "agents": [],
                "allocations": [],
                "bids": [],
                "metrics": {"stability_score": 0.95, "unmet_demand": 5.0, "risk_level": 0.05},
                "explanations": ["Hospital priority increased due to demand spike"],
            }
        }
