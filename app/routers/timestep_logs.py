"""API routes for timestep log management"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.mongo_db.connection import get_mongodb
from app.mongo_db.repository import SimulationRepository, TimestepLogRepository

router = APIRouter(prefix="/api/v1/timestep-logs", tags=["timestep-logs"])


class EventSummaryItem(BaseModel):
    type: str
    severity: float = Field(..., ge=0, le=1)


class TimestepLogCreate(BaseModel):
    simulation_id: str
    timestep: int = Field(..., ge=0)
    power_available: float = Field(..., ge=0)
    water_available: float = Field(..., ge=0)
    power_allocated: float = Field(..., ge=0)
    water_allocated: float = Field(..., ge=0)
    stability_score: float = Field(..., ge=0, le=1)
    risk_level: float = Field(..., ge=0, le=1)
    unmet_demand: float = Field(0.0, ge=0)
    allocation_efficiency: float = Field(0.0, ge=0, le=1)
    fairness_score: float = Field(0.0, ge=0, le=1)
    total_agents: int = Field(0, ge=0)
    agents_satisfied: int = Field(0, ge=0)
    agents_critical: int = Field(0, ge=0)
    events_occurred: int = Field(0, ge=0)
    events_summary: List[EventSummaryItem] = []
    total_bids: int = Field(0, ge=0)
    avg_utility_score: float = 0.0
    highest_utility_score: float = 0.0
    avg_trust_score: float = Field(0.5, ge=0, le=1)
    min_trust_score: float = Field(0.5, ge=0, le=1)
    max_trust_score: float = Field(0.5, ge=0, le=1)
    power_satisfaction_rate: float = Field(0.0, ge=0, le=1)
    water_satisfaction_rate: float = Field(0.0, ge=0, le=1)
    notes: Optional[str] = None


@router.post("/", response_model=dict)
def create_timestep_log(
    req: TimestepLogCreate,
    db=Depends(get_mongodb),
):
    """Create a timestep log record."""
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(req.simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    repo = TimestepLogRepository(db)
    log = repo.create(
        simulation_id=req.simulation_id,
        timestep=req.timestep,
        power_available=req.power_available,
        water_available=req.water_available,
        power_allocated=req.power_allocated,
        water_allocated=req.water_allocated,
        stability_score=req.stability_score,
        risk_level=req.risk_level,
        unmet_demand=req.unmet_demand,
        allocation_efficiency=req.allocation_efficiency,
        fairness_score=req.fairness_score,
        total_agents=req.total_agents,
        agents_satisfied=req.agents_satisfied,
        agents_critical=req.agents_critical,
        events_occurred=req.events_occurred,
        events_summary=[item.model_dump() for item in req.events_summary],
        total_bids=req.total_bids,
        avg_utility_score=req.avg_utility_score,
        highest_utility_score=req.highest_utility_score,
        avg_trust_score=req.avg_trust_score,
        min_trust_score=req.min_trust_score,
        max_trust_score=req.max_trust_score,
        power_satisfaction_rate=req.power_satisfaction_rate,
        water_satisfaction_rate=req.water_satisfaction_rate,
        notes=req.notes,
    )

    response = {
        "_id": str(log["_id"]),
        "simulation_id": str(log["simulation_id"]),
        "timestep": log["timestep"],
        "power_available": log["power_available"],
        "water_available": log["water_available"],
        "power_allocated": log["power_allocated"],
        "water_allocated": log["water_allocated"],
        "stability_score": log["stability_score"],
        "risk_level": log["risk_level"],
        "unmet_demand": log.get("unmet_demand", 0.0),
        "allocation_efficiency": log.get("allocation_efficiency", 0.0),
        "fairness_score": log.get("fairness_score", 0.0),
        "total_agents": log.get("total_agents", 0),
        "agents_satisfied": log.get("agents_satisfied", 0),
        "agents_critical": log.get("agents_critical", 0),
        "events_occurred": log.get("events_occurred", 0),
        "events_summary": log.get("events_summary", []),
        "total_bids": log.get("total_bids", 0),
        "avg_utility_score": log.get("avg_utility_score", 0.0),
        "highest_utility_score": log.get("highest_utility_score", 0.0),
        "avg_trust_score": log.get("avg_trust_score", 0.5),
        "min_trust_score": log.get("min_trust_score", 0.5),
        "max_trust_score": log.get("max_trust_score", 0.5),
        "power_satisfaction_rate": log.get("power_satisfaction_rate", 0.0),
        "water_satisfaction_rate": log.get("water_satisfaction_rate", 0.0),
        "created_at": log.get("created_at"),
        "updated_at": log.get("updated_at"),
    }
    if log.get("notes") is not None:
        response["notes"] = log["notes"]

    return response


@router.get("/", response_model=list[dict])
def list_timestep_logs(
    simulation_id: str,
    timestep: Optional[int] = None,
    start_timestep: Optional[int] = None,
    end_timestep: Optional[int] = None,
    db=Depends(get_mongodb),
):
    """List timestep logs for a simulation, optionally filtered by timestep or range."""
    repo = TimestepLogRepository(db)

    if timestep is not None:
        log = repo.get_by_timestep(simulation_id, timestep)
        logs = [log] if log else []
    elif start_timestep is not None or end_timestep is not None:
        if start_timestep is None or end_timestep is None:
            raise HTTPException(status_code=400, detail="start_timestep and end_timestep are required together")
        logs = repo.get_range(simulation_id, start_timestep, end_timestep)
    else:
        logs = repo.get_by_simulation(simulation_id)

    return [
        {
            "_id": str(log["_id"]),
            "simulation_id": str(log["simulation_id"]),
            "timestep": log["timestep"],
            "power_available": log.get("power_available", 0.0),
            "water_available": log.get("water_available", 0.0),
            "power_allocated": log.get("power_allocated", 0.0),
            "water_allocated": log.get("water_allocated", 0.0),
            "stability_score": log.get("stability_score", 0.0),
            "risk_level": log.get("risk_level", 0.0),
            "unmet_demand": log.get("unmet_demand", 0.0),
            "allocation_efficiency": log.get("allocation_efficiency", 0.0),
            "fairness_score": log.get("fairness_score", 0.0),
            "total_agents": log.get("total_agents", 0),
            "agents_satisfied": log.get("agents_satisfied", 0),
            "agents_critical": log.get("agents_critical", 0),
            "events_occurred": log.get("events_occurred", 0),
            "events_summary": log.get("events_summary", []),
            "total_bids": log.get("total_bids", 0),
            "avg_utility_score": log.get("avg_utility_score", 0.0),
            "highest_utility_score": log.get("highest_utility_score", 0.0),
            "avg_trust_score": log.get("avg_trust_score", 0.5),
            "min_trust_score": log.get("min_trust_score", 0.5),
            "max_trust_score": log.get("max_trust_score", 0.5),
            "power_satisfaction_rate": log.get("power_satisfaction_rate", 0.0),
            "water_satisfaction_rate": log.get("water_satisfaction_rate", 0.0),
            "created_at": log.get("created_at"),
            "updated_at": log.get("updated_at"),
            **({"notes": log["notes"]} if log.get("notes") is not None else {}),
        }
        for log in logs
    ]
