"""API routes for event management"""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.mongo_db.connection import get_mongodb
from app.mongo_db.repository import EventRepository, SimulationRepository

router = APIRouter(prefix="/api/v1/events", tags=["events"])


class EventCreate(BaseModel):
    simulation_id: str
    timestep: int = Field(..., ge=0)
    event_type: Literal[
        "power_outage",
        "water_shortage",
        "demand_spike",
        "infrastructure_failure",
        "recovery",
    ]
    severity: float = Field(..., ge=0, le=1)
    affected_agent_type: Optional[Literal["hospital", "water", "power", "emergency"]] = None
    description: Optional[str] = None


@router.post("/", response_model=dict)
def create_event(
    req: EventCreate,
    db=Depends(get_mongodb),
):
    """Create a new event record"""
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(req.simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    event_repo = EventRepository(db)
    event = event_repo.create(
        simulation_id=req.simulation_id,
        timestep=req.timestep,
        event_type=req.event_type,
        severity=req.severity,
        affected_agent_type=req.affected_agent_type,
        description=req.description,
    )

    response = {
        "_id": str(event["_id"]),
        "simulation_id": str(event["simulation_id"]),
        "timestep": event["timestep"],
        "event_type": event["event_type"],
        "severity": event["severity"],
        "created_at": event.get("created_at"),
        "updated_at": event.get("updated_at"),
    }
    if event.get("affected_agent_type") is not None:
        response["affected_agent_type"] = event["affected_agent_type"]
    if event.get("description") is not None:
        response["description"] = event["description"]

    return response


@router.get("/", response_model=list[dict])
def list_events(
    simulation_id: str,
    timestep: Optional[int] = None,
    db=Depends(get_mongodb),
):
    """List events for a simulation, optionally filtered by timestep."""
    event_repo = EventRepository(db)

    if timestep is not None:
        events = event_repo.get_by_timestep(simulation_id, timestep)
        events = events if isinstance(events, list) else ([events] if events else [])
    else:
        events = event_repo.get_by_simulation(simulation_id)

    return [
        {
            "_id": str(event["_id"]),
            "simulation_id": str(event["simulation_id"]),
            "timestep": event["timestep"],
            "event_type": event["event_type"],
            "severity": event["severity"],
            "created_at": event.get("created_at"),
            "updated_at": event.get("updated_at"),
            **({"affected_agent_type": event["affected_agent_type"]} if event.get("affected_agent_type") is not None else {}),
            **({"description": event["description"]} if event.get("description") is not None else {}),
        }
        for event in events
    ]
