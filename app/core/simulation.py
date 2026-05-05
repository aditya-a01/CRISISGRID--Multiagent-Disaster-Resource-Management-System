"""Simulation engine - core orchestrator of crisis response system"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import math

from app.core.agent import Agent, AgentType, BehaviorProfile, MemoryEntry
from app.core.dependency_graph import DependencyGraph


class EventType(str, Enum):
    """Types of simulated disaster events"""
    POWER_OUTAGE = "power_outage"
    WATER_SHORTAGE = "water_shortage"
    DEMAND_SPIKE = "demand_spike"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    RECOVERY = "recovery"


@dataclass
class Event:
    """Disaster event in simulation"""
    event_type: EventType
    severity: float  # 0.0 to 1.0
    affected_agent_type: Optional[AgentType]
    description: str
    timestep: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_type": self.event_type.value,
            "severity": self.severity,
            "affected_agent_type": self.affected_agent_type.value if self.affected_agent_type else None,
            "description": self.description,
            "timestep": self.timestep,
        }


@dataclass
class SimulationMetrics:
    """Metrics snapshot at a timestep"""
    stability_score: float  # 0.0 to 1.0
    unmet_demand: float
    risk_level: float  # 0.0 to 1.0
    allocation_efficiency: float  # 0.0 to 1.0
    fairness_score: float  # 0.0 to 1.0


class SimulationEngine:
    """Orchestrates multi-agent crisis response simulation"""

    def __init__(
        self,
        simulation_id: int,
        name: str,
        total_timesteps: int,
        power_capacity: float = 1000.0,
        water_capacity: float = 500.0,
    ):
        self.simulation_id = simulation_id
        self.name = name
        self.total_timesteps = total_timesteps
        self.current_timestep = 0

        # Resources
        self.power_capacity = power_capacity
        self.water_capacity = water_capacity
        self.power_available = power_capacity
        self.water_available = water_capacity

        # Agents and state
        self.agents: List[Agent] = []
        self.agents_by_type: Dict[AgentType, List[Agent]] = {}
        self.events: List[Event] = []
        self.allocation_history: List[Dict] = []

        # Dependency management
        self.dependency_graph = DependencyGraph()

        # Metrics tracking
        self.metrics_history: List[SimulationMetrics] = []
        self.explanations: List[str] = []

    def add_agent(self, agent: Agent) -> None:
        """Register an agent in the simulation"""
        agent.agent_id = len(self.agents) + 1
        self.agents.append(agent)
        
        if agent.agent_type not in self.agents_by_type:
            self.agents_by_type[agent.agent_type] = []
        self.agents_by_type[agent.agent_type].append(agent)

    def trigger_random_event(self) -> Optional[Event]:
        """Generate random disaster event"""
        event_chance = 0.15  # 15% chance per timestep
        
        if random.random() > event_chance:
            return None

        event_type = random.choice(list(EventType))
        severity = random.uniform(0.3, 1.0)
        affected_type = random.choice(list(AgentType))

        event = Event(
            event_type=event_type,
            severity=severity,
            affected_agent_type=affected_type,
            description=f"{event_type.value} affects {affected_type.value}",
            timestep=self.current_timestep,
        )

        self.events.append(event)
        return event

    def apply_event(self, event: Event) -> None:
        """Apply event effects to simulation"""
        if event.event_type == EventType.POWER_OUTAGE:
            reduction = event.severity * 0.4
            self.power_available = self.power_available * (1.0 - reduction)
            self.explanations.append(
                f"Power outage: capacity reduced by {reduction*100:.0f}%"
            )

        elif event.event_type == EventType.WATER_SHORTAGE:
            reduction = event.severity * 0.5
            self.water_available = self.water_available * (1.0 - reduction)
            self.explanations.append(
                f"Water shortage: capacity reduced by {reduction*100:.0f}%"
            )

        elif event.event_type == EventType.DEMAND_SPIKE:
            for agent in self.agents_by_type.get(event.affected_agent_type or AgentType.EMERGENCY, []):
                spike = event.severity * agent.max_demand * 0.5
                agent.current_demand = min(agent.max_demand, agent.current_demand + spike)
            self.explanations.append(
                f"Demand spike for {event.affected_agent_type.value} services"
            )

        elif event.event_type == EventType.RECOVERY:
            # Gradual resource recovery
            recovery_rate = event.severity * 0.1
            self.power_available = min(
                self.power_capacity,
                self.power_available * (1.0 + recovery_rate),
            )
            self.water_available = min(
                self.water_capacity,
                self.water_available * (1.0 + recovery_rate),
            )
            self.explanations.append("Recovery phase: resources restoring")

    def collect_bids(self) -> List[Dict]:
        """Have all agents submit bids"""
        bids = []
        for agent in self.agents:
            utility = agent.calculate_utility(available_resources=self.power_available)
            bid = agent.submit_bid()
            
            bids.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.name,
                "agent_type": agent.agent_type.value,
                "demand": agent.current_demand,
                "bid": bid,
                "utility": utility,
            })

        return bids

    def allocate_resources(self) -> List[Dict]:
        """
        Allocate resources using utility-based bidding with fairness constraints.
        
        Returns:
            List of allocation records
        """
        allocations = []

        # Sort agents by adjusted priority (including dependency-based adjustments)
        allocation_status = {
            atype: (0.7 if atype != AgentType.HOSPITAL else 0.8)
            for atype in AgentType
        }
        
        priority_adjusted = self.dependency_graph.get_priority_adjusted_agents(
            self.agents, allocation_status
        )
        
        # Sort by priority then utility
        sorted_agents = sorted(
            priority_adjusted,
            key=lambda x: (x[1], x[0].calculate_utility()),
            reverse=True,
        )

        # Critical minimum requirements
        critical_minimums = {
            AgentType.HOSPITAL: 50.0,
            AgentType.POWER: 30.0,
            AgentType.WATER: 30.0,
        }

        # First pass: allocate critical minimums
        remaining_power = self.power_available
        remaining_water = self.water_available
        allocations_by_agent = {}

        for agent, _ in sorted_agents:
            min_allocation = critical_minimums.get(agent.agent_type, 10.0)
            target_alloc = min(min_allocation, agent.current_demand)
            
            # Allocate to both power and water proportionally
            water_need = target_alloc * 0.3
            power_need = target_alloc * 0.7

            water_alloc = min(water_need, remaining_water)
            power_alloc = min(power_need, remaining_power)

            total_alloc = water_alloc + power_alloc
            allocations_by_agent[agent.agent_id] = total_alloc

            remaining_power -= power_alloc
            remaining_water -= water_alloc

        # Second pass: allocate remaining resources based on priority
        for agent, _ in sorted_agents:
            current_alloc = allocations_by_agent.get(agent.agent_id, 0)
            unmet = agent.current_demand - current_alloc

            if unmet > 0 and (remaining_power > 0 or remaining_water > 0):
                water_need = unmet * 0.3
                power_need = unmet * 0.7
                
                water_alloc = min(water_need, remaining_water)
                power_alloc = min(power_need, remaining_power)
                
                allocations_by_agent[agent.agent_id] = current_alloc + water_alloc + power_alloc
                
                remaining_power -= power_alloc
                remaining_water -= water_alloc

        # Apply allocations and record
        for agent in self.agents:
            allocated = allocations_by_agent.get(agent.agent_id, 0)
            agent.receive_allocation(allocated, self.current_timestep)

            allocations.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.name,
                "agent_type": agent.agent_type.value,
                "requested": agent.current_demand,
                "allocated": allocated,
                "unmet": agent.unmet_demand,
                "satisfaction": (allocated / agent.current_demand) if agent.current_demand > 0 else 1.0,
            })

        return allocations

    def update_trust_scores(self) -> None:
        """Update trust scores based on fairness and cooperation"""
        total_demand = sum(a.current_demand for a in self.agents)
        total_allocation = sum(a.allocated_resources for a in self.agents)

        for agent in self.agents:
            # Fairness metric: did agent get fair share relative to demand?
            fair_share = agent.current_demand / total_demand if total_demand > 0 else 0
            actual_share = agent.allocated_resources / total_allocation if total_allocation > 0 else 0
            fairness = 1.0 - abs(fair_share - actual_share)
            fairness = max(0.0, min(1.0, fairness))

            # Cooperation metric: past satisfaction score
            if agent.satisfaction_history:
                cooperation = sum(agent.satisfaction_history[-5:]) / min(5, len(agent.satisfaction_history))
            else:
                cooperation = 0.5

            agent.update_trust_score(fairness, cooperation)

    def calculate_metrics(self) -> SimulationMetrics:
        """Calculate system metrics"""
        total_demand = sum(a.current_demand for a in self.agents)
        total_unmet = sum(a.unmet_demand for a in self.agents)
        total_allocated = sum(a.allocated_resources for a in self.agents)

        # Stability: how well can we meet demand?
        if total_demand > 0:
            allocation_efficiency = total_allocated / total_demand
        else:
            allocation_efficiency = 1.0

        stability_score = allocation_efficiency * 0.7 + sum(
            a.trust_score for a in self.agents
        ) / len(self.agents) * 0.3 if self.agents else 1.0
        stability_score = max(0.0, min(1.0, stability_score))

        # Risk level
        _, warnings = self.dependency_graph.detect_cascading_failure_risk(
            self.agents, self._get_allocation_status()
        )
        risk_level = len(warnings) * 0.2
        risk_level = min(1.0, risk_level)

        # Fairness: coefficient of variation in satisfaction
        if self.agents and any(a.satisfaction_history for a in self.agents):
            satisfactions = [a.satisfaction_history[-1] for a in self.agents if a.satisfaction_history]
            mean_satisfaction = sum(satisfactions) / len(satisfactions)
            variance = sum((s - mean_satisfaction) ** 2 for s in satisfactions) / len(satisfactions)
            fairness_score = 1.0 - min(1.0, math.sqrt(variance))
        else:
            fairness_score = 1.0

        return SimulationMetrics(
            stability_score=stability_score,
            unmet_demand=total_unmet,
            risk_level=risk_level,
            allocation_efficiency=allocation_efficiency,
            fairness_score=fairness_score,
        )

    def _get_allocation_status(self) -> Dict[AgentType, float]:
        """Get satisfaction ratio for each agent type"""
        status = {}
        for atype in AgentType:
            agents = self.agents_by_type.get(atype, [])
            if agents:
                avg_satisfaction = sum(
                    (a.allocated_resources / a.current_demand) if a.current_demand > 0 else 1.0
                    for a in agents
                ) / len(agents)
                status[atype] = min(1.0, avg_satisfaction)
            else:
                status[atype] = 0.5
        return status

    def execute_timestep(self) -> Dict:
        """Execute single timestep of simulation"""
        self.explanations = []

        # 1. Trigger random event
        event = self.trigger_random_event()
        if event:
            self.apply_event(event)

        # 2. Agents adjust behavior based on history
        for agent in self.agents:
            agent.adjust_behavior(self.current_timestep)

        # 3. Collect bids from agents
        bids = self.collect_bids()

        # 4. Allocate resources
        allocations = self.allocate_resources()

        # 5. Update trust scores
        self.update_trust_scores()

        # 6. Calculate metrics
        metrics = self.calculate_metrics()
        self.metrics_history.append(metrics)

        # Increment timestep
        self.current_timestep += 1

        return {
            "timestep": self.current_timestep - 1,
            "event": event.to_dict() if event else None,
            "bids": bids,
            "allocations": allocations,
            "metrics": {
                "stability_score": metrics.stability_score,
                "unmet_demand": metrics.unmet_demand,
                "risk_level": metrics.risk_level,
                "allocation_efficiency": metrics.allocation_efficiency,
                "fairness_score": metrics.fairness_score,
            },
            "explanations": self.explanations,
        }

    def get_state(self) -> Dict:
        """Get complete simulation state"""
        return {
            "simulation_id": self.simulation_id,
            "name": self.name,
            "current_timestep": self.current_timestep,
            "total_timesteps": self.total_timesteps,
            "power_available": self.power_available,
            "water_available": self.water_available,
            "power_capacity": self.power_capacity,
            "water_capacity": self.water_capacity,
            "agents": [a.get_state() for a in self.agents],
        }
