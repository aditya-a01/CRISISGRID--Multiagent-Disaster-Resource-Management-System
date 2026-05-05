"""API routes for allocation management"""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.mongo_db.connection import get_mongodb
from app.mongo_db.repository import AllocationRepository, AgentRepository, SimulationRepository

router = APIRouter(prefix="/api/v1/allocations", tags=["allocations"])


class AllocationCreate(BaseModel):
    simulation_id: str
    agent_id: str
    timestep: int = Field(..., ge=0)
    resource_type: Literal["power", "water"]
    allocated_amount: float = Field(..., ge=0)
    requested_amount: float = Field(..., ge=0)
    utility_score: float
    was_fulfilled: float = Field(..., ge=0, le=1)
    explanation: Optional[str] = None


@router.post("/", response_model=dict)
def create_allocation(
    req: AllocationCreate,
    db=Depends(get_mongodb),
):
    """Create a new allocation record"""
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(req.simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    agent_repo = AgentRepository(db)
    agent = agent_repo.get_by_id(req.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if str(agent.get("simulation_id")) != req.simulation_id:
        raise HTTPException(status_code=400, detail="Agent does not belong to simulation")

    alloc_repo = AllocationRepository(db)
    allocation = alloc_repo.create(
        simulation_id=req.simulation_id,
        agent_id=req.agent_id,
        timestep=req.timestep,
        resource_type=req.resource_type,
        allocated_amount=req.allocated_amount,
        requested_amount=req.requested_amount,
        utility_score=req.utility_score,
        was_fulfilled=req.was_fulfilled,
        explanation=req.explanation,
    )

    response = {
        "_id": str(allocation["_id"]),
        "simulation_id": str(allocation["simulation_id"]),
        "agent_id": str(allocation["agent_id"]),
        "timestep": allocation["timestep"],
        "resource_type": allocation["resource_type"],
        "allocated_amount": allocation["allocated_amount"],
        "requested_amount": allocation["requested_amount"],
        "utility_score": allocation["utility_score"],
        "was_fulfilled": allocation["was_fulfilled"],
        "created_at": allocation.get("created_at"),
        "updated_at": allocation.get("updated_at"),
    }
    if allocation.get("explanation") is not None:
        response["explanation"] = allocation["explanation"]

    return response


@router.get("/", response_model=list[dict])
def list_allocations(
    simulation_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    db=Depends(get_mongodb),
):
    """List allocations, optionally filtered by simulation or agent."""
    alloc_repo = AllocationRepository(db)

    if simulation_id and agent_id:
        allocations = alloc_repo.get_agent_allocation_history(
            simulation_id=simulation_id,
            agent_id=agent_id,
        )
    elif simulation_id:
        allocations = alloc_repo.get_by_simulation(simulation_id)
    else:
        allocations = []

    return [
        {
            "_id": str(allocation["_id"]),
            "simulation_id": str(allocation["simulation_id"]),
            "agent_id": str(allocation["agent_id"]),
            "timestep": allocation["timestep"],
            "resource_type": allocation["resource_type"],
            "allocated_amount": allocation["allocated_amount"],
            "requested_amount": allocation["requested_amount"],
            "utility_score": allocation["utility_score"],
            "was_fulfilled": allocation["was_fulfilled"],
            "created_at": allocation.get("created_at"),
            "updated_at": allocation.get("updated_at"),
            **({"explanation": allocation["explanation"]} if allocation.get("explanation") is not None else {}),
        }
        for allocation in allocations
    ]
