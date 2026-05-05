"""Repository pattern for database persistence"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func, and_
from app.models.simulation import Simulation
from app.models.agent import Agent as AgentModel
from app.models.allocation import Allocation
from app.models.event import Event
from app.models.timestep_log import TimestepLog


class SimulationRepository:
    """Database persistence for simulations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: Optional[str], total_timesteps: int) -> Simulation:
        """Create a new simulation"""
        sim = Simulation(
            name=name,
            description=description,
            total_timesteps=total_timesteps,
            power_available=1000.0,
            water_available=500.0,
        )
        self.db.add(sim)
        self.db.commit()
        self.db.refresh(sim)
        return sim

    def get_by_id(self, simulation_id: int) -> Optional[Simulation]:
        """Get simulation by ID"""
        return self.db.query(Simulation).filter(Simulation.id == simulation_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Simulation]:
        """Get all simulations with pagination"""
        return (
            self.db.query(Simulation)
            .order_by(desc(Simulation.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_state(
        self,
        simulation_id: int,
        current_timestep: int,
        power_available: float,
        water_available: float,
        is_running: bool = False,
        is_completed: bool = False,
        stability_score: float = 1.0,
        unmet_demand: float = 0.0,
        risk_level: float = 0.0,
    ) -> Simulation:
        """Update simulation state"""
        sim = self.get_by_id(simulation_id)
        if not sim:
            return None

        sim.current_timestep = current_timestep
        sim.power_available = power_available
        sim.water_available = water_available
        sim.is_running = is_running
        sim.is_completed = is_completed
        sim.stability_score = stability_score
        sim.unmet_demand = unmet_demand
        sim.risk_level = risk_level

        self.db.commit()
        self.db.refresh(sim)
        return sim

    def delete(self, simulation_id: int) -> bool:
        """Delete a simulation"""
        sim = self.get_by_id(simulation_id)
        if sim:
            self.db.delete(sim)
            self.db.commit()
            return True
        return False


class AgentRepository:
    """Database persistence for agents"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        simulation_id: int,
        agent_type: str,
        name: str,
        current_demand: float,
        max_demand: float,
        min_demand: float,
        priority_level: float,
    ) -> AgentModel:
        """Create a new agent"""
        agent = AgentModel(
            simulation_id=simulation_id,
            agent_type=agent_type,
            name=name,
            current_demand=current_demand,
            max_demand=max_demand,
            min_demand=min_demand,
            priority_level=priority_level,
        )
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_by_id(self, agent_id: int) -> Optional[AgentModel]:
        """Get agent by ID"""
        return self.db.query(AgentModel).filter(AgentModel.id == agent_id).first()

    def get_by_simulation(self, simulation_id: int) -> List[AgentModel]:
        """Get all agents for a simulation"""
        return self.db.query(AgentModel).filter(AgentModel.simulation_id == simulation_id).all()

    def update_state(
        self,
        agent_id: int,
        current_demand: float,
        allocated_resources: float,
        unmet_demand: float,
        trust_score: float,
        current_bid: float,
    ) -> AgentModel:
        """Update agent state"""
        agent = self.get_by_id(agent_id)
        if not agent:
            return None

        agent.current_demand = current_demand
        agent.allocated_resources = allocated_resources
        agent.unmet_demand = unmet_demand
        agent.trust_score = trust_score
        agent.current_bid = current_bid

        self.db.commit()
        self.db.refresh(agent)
        return agent

    def update_memory(self, agent_id: int, memory_log: List[Dict[str, Any]]) -> AgentModel:
        """Update agent memory log"""
        agent = self.get_by_id(agent_id)
        if agent:
            agent.memory_log = memory_log
            self.db.commit()
            self.db.refresh(agent)
        return agent


class AllocationRepository:
    """Database persistence for allocations"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        simulation_id: int,
        agent_id: int,
        timestep: int,
        resource_type: str,
        allocated_amount: float,
        requested_amount: float,
        utility_score: float,
        was_fulfilled: float,
    ) -> Allocation:
        """Create allocation record"""
        allocation = Allocation(
            simulation_id=simulation_id,
            agent_id=agent_id,
            timestep=timestep,
            resource_type=resource_type,
            allocated_amount=allocated_amount,
            requested_amount=requested_amount,
            utility_score=utility_score,
            was_fulfilled=was_fulfilled,
        )
        self.db.add(allocation)
        self.db.commit()
        self.db.refresh(allocation)
        return allocation

    def get_by_simulation(self, simulation_id: int) -> List[Allocation]:
        """Get all allocations for a simulation"""
        return self.db.query(Allocation).filter(Allocation.simulation_id == simulation_id).all()

    def get_by_timestep(self, simulation_id: int, timestep: int) -> List[Allocation]:
        """Get allocations for a specific timestep"""
        return self.db.query(Allocation).filter(
            (Allocation.simulation_id == simulation_id) & (Allocation.timestep == timestep)
        ).all()


class EventRepository:
    """Database persistence for events"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        simulation_id: int,
        timestep: int,
        event_type: str,
        severity: float,
        affected_agent_type: Optional[str],
        description: str,
    ) -> Event:
        """Create event record"""
        event = Event(
            simulation_id=simulation_id,
            timestep=timestep,
            event_type=event_type,
            severity=severity,
            affected_agent_type=affected_agent_type,
            description=description,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_by_simulation(self, simulation_id: int) -> List[Event]:
        """Get all events for a simulation"""
        return self.db.query(Event).filter(Event.simulation_id == simulation_id).all()

    def get_by_timestep(self, simulation_id: int, timestep: int) -> List[Event]:
        """Get events for a specific timestep"""
        return self.db.query(Event).filter(
            (Event.simulation_id == simulation_id) & (Event.timestep == timestep)
        ).all()


class TimestepLogRepository:
    """Database persistence for detailed timestep execution logs"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        simulation_id: int,
        timestep: int,
        power_available: float,
        water_available: float,
        power_allocated: float,
        water_allocated: float,
        stability_score: float,
        risk_level: float,
        unmet_demand: float = 0.0,
        allocation_efficiency: float = 0.0,
        fairness_score: float = 0.0,
        total_agents: int = 0,
        agents_satisfied: int = 0,
        agents_critical: int = 0,
        events_occurred: int = 0,
        events_summary: List[Dict] = None,
        total_bids: int = 0,
        avg_utility_score: float = 0.0,
        highest_utility_score: float = 0.0,
        avg_trust_score: float = 0.5,
        min_trust_score: float = 0.5,
        max_trust_score: float = 0.5,
        power_satisfaction_rate: float = 0.0,
        water_satisfaction_rate: float = 0.0,
        notes: Optional[str] = None,
    ) -> TimestepLog:
        """Create a timestep log record"""
        if events_summary is None:
            events_summary = []

        log = TimestepLog(
            simulation_id=simulation_id,
            timestep=timestep,
            power_available=power_available,
            water_available=water_available,
            power_allocated=power_allocated,
            water_allocated=water_allocated,
            stability_score=stability_score,
            risk_level=risk_level,
            unmet_demand=unmet_demand,
            allocation_efficiency=allocation_efficiency,
            fairness_score=fairness_score,
            total_agents=total_agents,
            agents_satisfied=agents_satisfied,
            agents_critical=agents_critical,
            events_occurred=events_occurred,
            events_summary=events_summary,
            total_bids=total_bids,
            avg_utility_score=avg_utility_score,
            highest_utility_score=highest_utility_score,
            avg_trust_score=avg_trust_score,
            min_trust_score=min_trust_score,
            max_trust_score=max_trust_score,
            power_satisfaction_rate=power_satisfaction_rate,
            water_satisfaction_rate=water_satisfaction_rate,
            notes=notes,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_by_simulation(self, simulation_id: int) -> List[TimestepLog]:
        """Get all timestep logs for a simulation"""
        return (
            self.db.query(TimestepLog)
            .filter(TimestepLog.simulation_id == simulation_id)
            .order_by(asc(TimestepLog.timestep))
            .all()
        )

    def get_by_timestep(self, simulation_id: int, timestep: int) -> Optional[TimestepLog]:
        """Get timestep log for specific timestep"""
        return self.db.query(TimestepLog).filter(
            (TimestepLog.simulation_id == simulation_id) & (TimestepLog.timestep == timestep)
        ).first()

    def get_range(self, simulation_id: int, start_timestep: int, end_timestep: int) -> List[TimestepLog]:
        """Get timestep logs for a range of timesteps"""
        return (
            self.db.query(TimestepLog)
            .filter(
                (TimestepLog.simulation_id == simulation_id)
                & (TimestepLog.timestep >= start_timestep)
                & (TimestepLog.timestep <= end_timestep)
            )
            .order_by(asc(TimestepLog.timestep))
            .all()
        )


class AnalyticsRepository:
    """Advanced queries for historical analysis and performance metrics"""

    def __init__(self, db: Session):
        self.db = db

    def get_agent_allocation_history(
        self, simulation_id: int, agent_id: int
    ) -> List[Dict[str, Any]]:
        """Get complete allocation history for an agent"""
        allocations = (
            self.db.query(Allocation)
            .filter(
                (Allocation.simulation_id == simulation_id) & (Allocation.agent_id == agent_id)
            )
            .order_by(asc(Allocation.timestep))
            .all()
        )
        return [
            {
                "timestep": a.timestep,
                "resource": a.resource_type,
                "requested": a.requested_amount,
                "allocated": a.allocated_amount,
                "fulfilled": a.was_fulfilled,
                "utility": a.utility_score,
            }
            for a in allocations
        ]

    def get_agent_satisfaction_trend(
        self, simulation_id: int, agent_id: int
    ) -> List[Tuple[int, float]]:
        """Get satisfaction trend for agent (timestep, satisfaction_rate)"""
        allocations = (
            self.db.query(Allocation.timestep, Allocation.was_fulfilled)
            .filter(
                (Allocation.simulation_id == simulation_id) & (Allocation.agent_id == agent_id)
            )
            .order_by(asc(Allocation.timestep))
            .all()
        )
        return [(a[0], a[1]) for a in allocations]

    def get_resource_efficiency_by_type(
        self, simulation_id: int
    ) -> Dict[str, Dict[str, float]]:
        """Get allocation efficiency metrics by resource type"""
        results = (
            self.db.query(
                Allocation.resource_type,
                func.sum(Allocation.allocated_amount).label("total_allocated"),
                func.sum(Allocation.requested_amount).label("total_requested"),
                func.avg(Allocation.was_fulfilled).label("avg_fulfillment"),
            )
            .filter(Allocation.simulation_id == simulation_id)
            .group_by(Allocation.resource_type)
            .all()
        )

        efficiency = {}
        for resource, allocated, requested, fulfillment in results:
            efficiency[resource] = {
                "total_allocated": float(allocated) if allocated else 0.0,
                "total_requested": float(requested) if requested else 0.0,
                "efficiency": float(fulfillment) if fulfillment else 0.0,
            }
        return efficiency

    def get_agent_trust_evolution(
        self, simulation_id: int, agent_id: int
    ) -> List[Dict[str, Any]]:
        """Get trust score evolution for an agent across timesteps"""
        agents = (
            self.db.query(AgentModel.trust_score)
            .filter((AgentModel.simulation_id == simulation_id) & (AgentModel.id == agent_id))
            .all()
        )
        # Note: This gets current trust. For true evolution, need to store trust per timestep.
        # Recommend adding trust_score column to TimestepLog
        return [{"current_trust": float(a[0]) if a[0] else 0.5} for a in agents]

    def get_fairness_metrics(self, simulation_id: int) -> Dict[str, float]:
        """Get fairness metrics for entire simulation"""
        logs = self.db.query(TimestepLog).filter(
            TimestepLog.simulation_id == simulation_id
        ).all()

        if not logs:
            return {
                "avg_fairness": 0.0,
                "min_fairness": 0.0,
                "max_fairness": 0.0,
            }

        fairness_scores = [log.fairness_score for log in logs]
        return {
            "avg_fairness": sum(fairness_scores) / len(fairness_scores),
            "min_fairness": min(fairness_scores),
            "max_fairness": max(fairness_scores),
        }

    def get_event_impact_analysis(self, simulation_id: int) -> Dict[str, Any]:
        """Analyze impact of events on system stability"""
        events = (
            self.db.query(Event)
            .filter(Event.simulation_id == simulation_id)
            .order_by(asc(Event.timestep))
            .all()
        )

        logs = self.db.query(TimestepLog).filter(
            TimestepLog.simulation_id == simulation_id
        ).all()

        event_impacts = {}
        for event in events:
            if event.timestep < len(logs):
                log = logs[event.timestep]
                event_type = event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type)
                if event_type not in event_impacts:
                    event_impacts[event_type] = {
                        "count": 0,
                        "total_severity": 0.0,
                        "avg_risk_after": 0.0,
                    }
                event_impacts[event_type]["count"] += 1
                event_impacts[event_type]["total_severity"] += event.severity
                event_impacts[event_type]["avg_risk_after"] += log.risk_level

        # Calculate averages
        for event_type in event_impacts:
            count = event_impacts[event_type]["count"]
            event_impacts[event_type]["avg_severity"] = event_impacts[event_type]["total_severity"] / count
            event_impacts[event_type]["avg_risk_after"] /= count

        return event_impacts

    def get_stability_trend(self, simulation_id: int) -> List[Dict[str, Any]]:
        """Get stability score trend across all timesteps"""
        logs = (
            self.db.query(
                TimestepLog.timestep,
                TimestepLog.stability_score,
                TimestepLog.risk_level,
                TimestepLog.unmet_demand,
            )
            .filter(TimestepLog.simulation_id == simulation_id)
            .order_by(asc(TimestepLog.timestep))
            .all()
        )

        return [
            {
                "timestep": log[0],
                "stability": float(log[1]),
                "risk": float(log[2]),
                "unmet_demand": float(log[3]),
            }
            for log in logs
        ]

    def get_critical_agents_timeline(self, simulation_id: int) -> List[Dict[str, Any]]:
        """Get timeline of when agents became critical (unmet > 50%)"""
        logs = (
            self.db.query(TimestepLog.timestep, TimestepLog.agents_critical)
            .filter(TimestepLog.simulation_id == simulation_id)
            .order_by(asc(TimestepLog.timestep))
            .all()
        )

        return [
            {
                "timestep": log[0],
                "critical_count": log[1],
            }
            for log in logs
        ]

    def get_high_trust_agents(self, simulation_id: int, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Get agents with trust score above threshold"""
        agents = (
            self.db.query(AgentModel)
            .filter(
                (AgentModel.simulation_id == simulation_id)
                & (AgentModel.trust_score >= threshold)
            )
            .all()
        )

        return [
            {
                "id": a.id,
                "name": a.name,
                "type": a.agent_type.value if hasattr(a.agent_type, 'value') else str(a.agent_type),
                "trust_score": float(a.trust_score),
                "cooperation_level": float(a.cooperation_level),
            }
            for a in agents
        ]

    def get_simulation_summary(self, simulation_id: int) -> Dict[str, Any]:
        """Get comprehensive summary of simulation performance"""
        sim = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not sim:
            return {}

        logs = self.db.query(TimestepLog).filter(
            TimestepLog.simulation_id == simulation_id
        ).all()

        if not logs:
            return {
                "simulation_id": simulation_id,
                "name": sim.name,
                "timesteps_executed": 0,
                "status": "no_data",
            }

        stability_scores = [log.stability_score for log in logs]
        risk_levels = [log.risk_level for log in logs]
        fairness_scores = [log.fairness_score for log in logs]
        efficiency = [log.allocation_efficiency for log in logs]

        return {
            "simulation_id": simulation_id,
            "name": sim.name,
            "description": sim.description,
            "timesteps_executed": len(logs),
            "status": "completed" if sim.is_completed else "running",
            "stability": {
                "avg": sum(stability_scores) / len(stability_scores),
                "min": min(stability_scores),
                "max": max(stability_scores),
            },
            "risk": {
                "avg": sum(risk_levels) / len(risk_levels),
                "min": min(risk_levels),
                "max": max(risk_levels),
            },
            "fairness": {
                "avg": sum(fairness_scores) / len(fairness_scores),
                "min": min(fairness_scores),
                "max": max(fairness_scores),
            },
            "efficiency": {
                "avg": sum(efficiency) / len(efficiency),
                "min": min(efficiency),
                "max": max(efficiency),
            },
        }
