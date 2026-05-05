"""API routes for simulation management"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.mongo_db.connection import get_mongodb
from app.mongo_db.repository import (
    SimulationRepository,
    AgentRepository,
    AllocationRepository,
    EventRepository,
    TimestepLogRepository,
)
from app.schemas.simulation import SimulationSchema, SimulationCreateSchema
from app.schemas.agent import AgentSchema
from app.schemas.allocation import AllocationSchema
from app.schemas.response import SimulationStepResponse, MetricsSchema

from app.core.simulation import SimulationEngine
from app.core.agent import Agent as CoreAgent, AgentType as CoreAgentType, BehaviorProfile as CoreBehaviorProfile

router = APIRouter(prefix="/api/v1/simulations", tags=["simulations"])


# ── Helper: build a SimulationEngine from DB state ─────────────────────────────
def _build_engine(sim: dict, db_agents: list) -> SimulationEngine:
    """Instantiate a SimulationEngine populated with DB state."""
    engine = SimulationEngine(
        simulation_id=str(sim["_id"]),
        name=sim["name"],
        total_timesteps=sim["total_timesteps"],
        power_capacity=sim.get("power_available", 1000.0),
        water_capacity=sim.get("water_available", 500.0),
    )
    engine.current_timestep = sim.get("current_timestep", 0)
    engine.power_available = sim.get("power_available", 1000.0)
    engine.water_available = sim.get("water_available", 500.0)

    # Map string agent_type -> CoreAgentType
    type_map = {
        "hospital": CoreAgentType.HOSPITAL,
        "water": CoreAgentType.WATER,
        "power": CoreAgentType.POWER,
        "emergency": CoreAgentType.EMERGENCY,
    }
    profile_map = {
        "cooperative": CoreBehaviorProfile.COOPERATIVE,
        "competitive": CoreBehaviorProfile.COMPETITIVE,
        "adaptive": CoreBehaviorProfile.ADAPTIVE,
    }

    for ag_doc in db_agents:
        core_agent = CoreAgent(
            agent_id=0,  # will be reassigned by add_agent
            agent_type=type_map.get(ag_doc["agent_type"], CoreAgentType.EMERGENCY),
            name=ag_doc["name"],
            current_demand=ag_doc.get("current_demand", 0),
            max_demand=ag_doc.get("max_demand", 100),
            min_demand=ag_doc.get("min_demand", 10),
            priority_level=ag_doc.get("priority_level", 1.0),
            behavior_profile=profile_map.get(ag_doc.get("behavior_profile", "adaptive"), CoreBehaviorProfile.ADAPTIVE),
            risk_tolerance=ag_doc.get("risk_tolerance", 0.5),
            cooperation_level=ag_doc.get("cooperation_level", 0.5),
            urgency_bias=ag_doc.get("urgency_bias", 0.5),
            trust_score=ag_doc.get("trust_score", 0.5),
            allocated_resources=ag_doc.get("allocated_resources", 0.0),
            dependency_factor=ag_doc.get("dependency_factor", 1.0),
        )
        # Attach the Mongo _id so we can persist updates back
        core_agent._mongo_id = str(ag_doc["_id"])
        engine.add_agent(core_agent)

    return engine


def _format_sim(sim: dict) -> dict:
    """Standard simulation dict formatter."""
    return {
        "_id": str(sim["_id"]),
        "name": sim["name"],
        "description": sim.get("description"),
        "total_timesteps": sim["total_timesteps"],
        "current_timestep": sim.get("current_timestep", 0),
        "is_running": sim.get("is_running", False),
        "is_completed": sim.get("is_completed", False),
        "power_available": sim.get("power_available", 1000),
        "water_available": sim.get("water_available", 500),
        "stability_score": sim.get("stability_score", 1.0),
        "unmet_demand": sim.get("unmet_demand", 0),
        "risk_level": sim.get("risk_level", 0),
        "created_at": sim.get("created_at"),
        "updated_at": sim.get("updated_at"),
    }


# ── CRUD routes ────────────────────────────────────────────────────────────────

@router.post("/", response_model=dict)
def create_simulation(
    req: SimulationCreateSchema,
    db = Depends(get_mongodb),
):
    """Create a new crisis response simulation"""
    repo = SimulationRepository(db)
    sim = repo.create(
        name=req.name,
        description=req.description,
        total_timesteps=req.total_timesteps,
    )
    return _format_sim(sim)


@router.get("/", response_model=List[dict])
def list_simulations(
    skip: int = 0,
    limit: int = 20,
    db = Depends(get_mongodb),
):
    """List all simulations"""
    repo = SimulationRepository(db)
    sims = repo.get_all(skip=skip, limit=limit)
    return [_format_sim(sim) for sim in sims]


@router.get("/{simulation_id}", response_model=dict)
def get_simulation(
    simulation_id: str,
    db = Depends(get_mongodb),
):
    """Get a specific simulation by ID"""
    repo = SimulationRepository(db)
    sim = repo.get_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return _format_sim(sim)


@router.post("/{simulation_id}/agents", response_model=dict)
def add_agent_to_simulation(
    simulation_id: str,
    agent_type: str,
    name: str,
    current_demand: float,
    max_demand: float,
    min_demand: float,
    priority_level: float = 1.0,
    behavior_profile: str = "cooperative",
    db = Depends(get_mongodb),
):
    """Add an agent to a simulation"""
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    agent_repo = AgentRepository(db)
    agent = agent_repo.create(
        simulation_id=simulation_id,
        agent_type=agent_type,
        name=name,
        current_demand=current_demand,
        max_demand=max_demand,
        min_demand=min_demand,
        priority_level=priority_level,
        behavior_profile=behavior_profile,
    )
    return {
        "_id": str(agent["_id"]),
        "name": agent["name"],
        "agent_type": agent["agent_type"],
        "priority_level": agent.get("priority_level", 1.0),
        "current_demand": agent.get("current_demand", 0),
        "allocated_resources": agent.get("allocated_resources", 0),
    }


@router.get("/{simulation_id}/agents", response_model=List[dict])
def get_simulation_agents(
    simulation_id: str,
    db = Depends(get_mongodb),
):
    """Get all agents in a simulation"""
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    agent_repo = AgentRepository(db)
    agents = agent_repo.get_by_simulation(simulation_id)
    return [
        {
            "_id": str(agent["_id"]),
            "simulation_id": str(agent["simulation_id"]),
            "name": agent["name"],
            "agent_type": agent["agent_type"],
            "current_demand": agent.get("current_demand", 0),
            "allocated_resources": agent.get("allocated_resources", 0),
            "trust_score": agent.get("trust_score", 0.5),
            "priority_level": agent.get("priority_level", 1.0),
            "behavior_profile": agent.get("behavior_profile", "adaptive"),
            "risk_tolerance": agent.get("risk_tolerance", 0.5),
            "cooperation_level": agent.get("cooperation_level", 0.5),
        }
        for agent in agents
    ]


@router.delete("/{simulation_id}", response_model=dict)
def delete_simulation(
    simulation_id: str,
    db = Depends(get_mongodb),
):
    """Delete a simulation and all its data"""
    repo = SimulationRepository(db)
    success = repo.delete(simulation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {"status": "deleted", "simulation_id": simulation_id}


# ── Step route ─────────────────────────────────────────────────────────────────

@router.post("/{simulation_id}/step", response_model=dict)
def execute_simulation_step(
    simulation_id: str,
    db = Depends(get_mongodb),
):
    """
    Execute a single simulation timestep.

    Loads simulation + agents from DB, runs the core SimulationEngine for one
    tick, persists all results (agent state, allocations, events, timestep log,
    simulation state) back to MongoDB, and returns the full step response
    expected by the frontend.
    """
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    if sim.get("is_completed", False):
        raise HTTPException(status_code=400, detail="Simulation already completed")

    # Load agents from DB
    agent_repo = AgentRepository(db)
    db_agents = agent_repo.get_by_simulation(simulation_id)
    if not db_agents:
        raise HTTPException(status_code=400, detail="No agents in simulation — add agents first")

    # Build engine from DB state
    engine = _build_engine(sim, db_agents)

    # Execute one timestep
    step_result = engine.execute_timestep()

    # Determine completion
    is_completed = engine.current_timestep >= engine.total_timesteps

    # ── Persist results back to MongoDB ──

    # 1. Update simulation state
    sim_repo.update_state(
        simulation_id,
        current_timestep=engine.current_timestep,
        power_available=engine.power_available,
        water_available=engine.water_available,
        is_running=not is_completed,
        is_completed=is_completed,
        stability_score=step_result["metrics"]["stability_score"],
        unmet_demand=step_result["metrics"]["unmet_demand"],
        risk_level=step_result["metrics"]["risk_level"],
    )

    # 2. Update each agent's state in DB
    for i, core_agent in enumerate(engine.agents):
        mongo_id = core_agent._mongo_id
        agent_repo.update_state(
            agent_id=mongo_id,
            current_demand=core_agent.current_demand,
            allocated_resources=core_agent.allocated_resources,
            unmet_demand=core_agent.unmet_demand,
            trust_score=core_agent.trust_score,
            current_bid=core_agent.current_bid,
        )

    # 3. Persist allocations
    alloc_repo = AllocationRepository(db)
    for alloc in step_result["allocations"]:
        # Find corresponding core agent to get mongo id
        agent_idx = alloc["agent_id"] - 1  # agent_id is 1-indexed
        if 0 <= agent_idx < len(engine.agents):
            mongo_agent_id = engine.agents[agent_idx]._mongo_id
        else:
            continue

        satisfaction = alloc.get("satisfaction", 0)
        alloc_repo.create(
            simulation_id=simulation_id,
            agent_id=mongo_agent_id,
            timestep=step_result["timestep"],
            resource_type="power",
            allocated_amount=alloc["allocated"] * 0.7,
            requested_amount=alloc["requested"] * 0.7,
            utility_score=next((b["utility"] for b in step_result["bids"] if b["agent_id"] == alloc["agent_id"]), 0),
            was_fulfilled=satisfaction,
            explanation=f"{alloc['agent_name']} satisfied {satisfaction*100:.1f}%",
        )
        alloc_repo.create(
            simulation_id=simulation_id,
            agent_id=mongo_agent_id,
            timestep=step_result["timestep"],
            resource_type="water",
            allocated_amount=alloc["allocated"] * 0.3,
            requested_amount=alloc["requested"] * 0.3,
            utility_score=next((b["utility"] for b in step_result["bids"] if b["agent_id"] == alloc["agent_id"]), 0),
            was_fulfilled=satisfaction,
            explanation=f"{alloc['agent_name']} satisfied {satisfaction*100:.1f}%",
        )

    # 4. Persist event if one occurred
    event_data = step_result.get("event")
    if event_data:
        event_repo = EventRepository(db)
        event_repo.create(
            simulation_id=simulation_id,
            timestep=step_result["timestep"],
            event_type=event_data["event_type"],
            severity=event_data["severity"],
            affected_agent_type=event_data.get("affected_agent_type"),
            description=event_data.get("description"),
        )

    # 5. Persist timestep log
    ts_repo = TimestepLogRepository(db)
    metrics = step_result["metrics"]
    total_demand = sum(a["requested"] for a in step_result["allocations"])
    total_alloc = sum(a["allocated"] for a in step_result["allocations"])
    agents_satisfied = sum(1 for a in step_result["allocations"] if a.get("satisfaction", 0) >= 0.8)
    agents_critical = sum(1 for a in step_result["allocations"] if a.get("satisfaction", 0) < 0.3)
    trust_scores = [a.trust_score for a in engine.agents]

    events_summary = []
    if event_data:
        events_summary = [{"type": event_data["event_type"], "severity": event_data["severity"]}]

    ts_repo.create(
        simulation_id=simulation_id,
        timestep=step_result["timestep"],
        power_available=engine.power_available,
        water_available=engine.water_available,
        power_allocated=total_alloc * 0.7,
        water_allocated=total_alloc * 0.3,
        stability_score=metrics["stability_score"],
        risk_level=metrics["risk_level"],
        unmet_demand=metrics["unmet_demand"],
        allocation_efficiency=metrics["allocation_efficiency"],
        fairness_score=metrics["fairness_score"],
        total_agents=len(engine.agents),
        agents_satisfied=agents_satisfied,
        agents_critical=agents_critical,
        events_occurred=1 if event_data else 0,
        events_summary=events_summary,
        total_bids=len(step_result["bids"]),
        avg_utility_score=sum(b["utility"] for b in step_result["bids"]) / max(len(step_result["bids"]), 1),
        highest_utility_score=max((b["utility"] for b in step_result["bids"]), default=0),
        avg_trust_score=sum(trust_scores) / max(len(trust_scores), 1),
        min_trust_score=min(trust_scores) if trust_scores else 0.5,
        max_trust_score=max(trust_scores) if trust_scores else 0.5,
        power_satisfaction_rate=min(1.0, engine.power_available / engine.power_capacity) if engine.power_capacity > 0 else 0,
        water_satisfaction_rate=min(1.0, engine.water_available / engine.water_capacity) if engine.water_capacity > 0 else 0,
    )

    # ── Build response for frontend ──
    # Re-read sim state for the response
    updated_sim = sim_repo.get_by_id(simulation_id)

    state_response = {
        "simulation_id": simulation_id,
        "name": updated_sim["name"],
        "current_timestep": updated_sim.get("current_timestep", 0),
        "total_timesteps": updated_sim["total_timesteps"],
        "is_running": updated_sim.get("is_running", False),
        "is_completed": updated_sim.get("is_completed", False),
        "power_available": updated_sim.get("power_available", 1000),
        "water_available": updated_sim.get("water_available", 500),
    }

    agents_response = [
        {
            "id": a.agent_id,
            "name": a.name,
            "agent_type": a.agent_type.value,
            "current_demand": a.current_demand,
            "allocated_resources": a.allocated_resources,
            "current_bid": a.current_bid,
            "unmet_demand": a.unmet_demand,
            "trust_score": a.trust_score,
            "priority_level": a.priority_level,
            "risk_tolerance": a.risk_tolerance,
            "cooperation_level": a.cooperation_level,
            "behavior_profile": a.behavior_profile.value,
        }
        for a in engine.agents
    ]

    return {
        "state": state_response,
        "agents": agents_response,
        "allocations": step_result["allocations"],
        "bids": step_result["bids"],
        "metrics": step_result["metrics"],
        "event": step_result.get("event"),
        "explanations": step_result.get("explanations", []),
    }


# ── Metrics route ──────────────────────────────────────────────────────────────

@router.get("/{simulation_id}/metrics", response_model=dict)
def get_simulation_metrics(
    simulation_id: str,
    db = Depends(get_mongodb),
):
    """Get current metrics for a simulation"""
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    total = sim.get("total_timesteps", 100)
    current = sim.get("current_timestep", 0)

    return {
        "stability_score": sim.get("stability_score", 1.0),
        "unmet_demand": sim.get("unmet_demand", 0),
        "risk_level": sim.get("risk_level", 0),
        "allocation_efficiency": 1.0 - (sim.get("unmet_demand", 0) / max(total, 1)),
        "fairness_score": sim.get("stability_score", 1.0),
        "current_timestep": current,
        "total_timesteps": total,
        "progress": current / total if total > 0 else 0,
    }


# ── Allocations sub-route ─────────────────────────────────────────────────────

@router.get("/{simulation_id}/allocations", response_model=List[dict])
def get_simulation_allocations(
    simulation_id: str,
    timestep: Optional[int] = None,
    db = Depends(get_mongodb),
):
    """Get allocation records for a simulation, optionally filtered by timestep"""
    sim_repo = SimulationRepository(db)
    sim = sim_repo.get_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")

    alloc_repo = AllocationRepository(db)

    if timestep is not None:
        allocations = alloc_repo.get_by_timestep(simulation_id, timestep)
    else:
        allocations = alloc_repo.get_by_simulation(simulation_id)

    return [
        {
            "_id": str(a["_id"]),
            "simulation_id": str(a["simulation_id"]),
            "agent_id": str(a["agent_id"]),
            "timestep": a["timestep"],
            "resource_type": a["resource_type"],
            "allocated_amount": a["allocated_amount"],
            "requested_amount": a["requested_amount"],
            "utility_score": a["utility_score"],
            "was_fulfilled": a["was_fulfilled"],
            "created_at": a.get("created_at"),
            "updated_at": a.get("updated_at"),
            **({
                "explanation": a["explanation"]
            } if a.get("explanation") is not None else {}),
        }
        for a in allocations
    ]
