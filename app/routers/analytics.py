"""API routes for analytics queries"""

from fastapi import APIRouter, Depends, HTTPException

from app.mongo_db.analytics import AnalyticsRepository
from app.mongo_db.connection import get_mongodb
from app.mongo_db.repository import SimulationRepository

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


def _ensure_simulation(db, simulation_id: str) -> None:
    repo = SimulationRepository(db)
    sim = repo.get_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")


@router.get("/summary", response_model=dict)
def get_simulation_summary(
    simulation_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_simulation_summary(simulation_id)


@router.get("/stability", response_model=list[dict])
def get_stability_trend(
    simulation_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_stability_trend(simulation_id)


@router.get("/fairness", response_model=dict)
def get_fairness_metrics(
    simulation_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_fairness_metrics(simulation_id)


@router.get("/event-impact", response_model=dict)
def get_event_impact(
    simulation_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_event_impact_analysis(simulation_id)


@router.get("/resource-efficiency", response_model=dict)
def get_resource_efficiency(
    simulation_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_resource_efficiency_by_type(simulation_id)


@router.get("/agent-allocation-history", response_model=list[dict])
def get_agent_allocation_history(
    simulation_id: str,
    agent_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_agent_allocation_history(simulation_id, agent_id)


@router.get("/agent-satisfaction", response_model=list[list])
def get_agent_satisfaction_trend(
    simulation_id: str,
    agent_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_agent_satisfaction_trend(simulation_id, agent_id)


@router.get("/critical-agents", response_model=list[dict])
def get_critical_agents_timeline(
    simulation_id: str,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_critical_agents_timeline(simulation_id)


@router.get("/high-trust-agents", response_model=list[dict])
def get_high_trust_agents(
    simulation_id: str,
    threshold: float = 0.8,
    db=Depends(get_mongodb),
):
    _ensure_simulation(db, simulation_id)
    repo = AnalyticsRepository(db)
    return repo.get_high_trust_agents(simulation_id, threshold)
