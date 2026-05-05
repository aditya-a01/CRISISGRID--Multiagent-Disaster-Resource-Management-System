"""Dependency graph and constraint management"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from app.core.agent import Agent, AgentType


@dataclass
class DependencyEdge:
    """Edge in dependency graph: source depends on target"""
    source: AgentType
    target: AgentType
    impact: float = 1.0  # How much target affects source (0.0 to 1.0)


class DependencyGraph:
    """Manages dependencies between agents to prevent cascading failures"""

    # Default crisis response dependency chain
    DEFAULT_DEPENDENCIES = [
        DependencyEdge(AgentType.WATER, AgentType.POWER, impact=0.8),
        DependencyEdge(AgentType.HOSPITAL, AgentType.POWER, impact=1.0),
        DependencyEdge(AgentType.HOSPITAL, AgentType.WATER, impact=0.9),
        DependencyEdge(AgentType.EMERGENCY, AgentType.POWER, impact=0.6),
        DependencyEdge(AgentType.EMERGENCY, AgentType.WATER, impact=0.7),
    ]

    def __init__(self):
        self.edges: List[DependencyEdge] = self.DEFAULT_DEPENDENCIES.copy()
        self._dependency_cache: Dict[AgentType, List[Tuple[AgentType, float]]] = {}
        self._rebuild_cache()

    def _rebuild_cache(self):
        """Rebuild the dependency lookup cache"""
        self._dependency_cache = {}
        for edge in self.edges:
            if edge.source not in self._dependency_cache:
                self._dependency_cache[edge.source] = []
            self._dependency_cache[edge.source].append((edge.target, edge.impact))

    def get_dependencies(self, agent_type: AgentType) -> List[Tuple[AgentType, float]]:
        """Get all agents that this agent depends on with impact factors"""
        return self._dependency_cache.get(agent_type, [])

    def adjust_priority_for_dependencies(
        self,
        agent: Agent,
        allocation_status: Dict[AgentType, float],
    ) -> float:
        """
        Adjust agent's effective priority based on its dependencies' satisfaction.
        
        Args:
            agent: The agent to adjust priority for
            allocation_status: Dict of AgentType -> satisfaction_ratio (0.0 to 1.0)
        
        Returns:
            Adjusted priority level
        """
        dependencies = self.get_dependencies(agent.agent_type)
        
        if not dependencies:
            return agent.priority_level

        # Calculate dependency satisfaction
        dependency_satisfaction = 0.0
        total_impact = 0.0

        for dep_type, impact in dependencies:
            satisfaction = allocation_status.get(dep_type, 0.5)
            dependency_satisfaction += satisfaction * impact
            total_impact += impact

        if total_impact > 0:
            avg_dep_satisfaction = dependency_satisfaction / total_impact
        else:
            avg_dep_satisfaction = 1.0

        # Boost priority if dependencies are poorly satisfied
        # This prevents cascading failures
        if avg_dep_satisfaction < 0.4:
            boost = (1.0 - avg_dep_satisfaction) * 0.5  # Up to 50% boost
            return agent.priority_level * (1.0 + boost)
        
        return agent.priority_level

    def detect_cascading_failure_risk(
        self,
        agents: List[Agent],
        allocation_status: Dict[AgentType, float],
    ) -> Tuple[float, List[str]]:
        """
        Detect risk of cascading failures.
        
        Returns:
            (risk_score, list_of_warnings)
        """
        risk_score = 0.0
        warnings = []

        # Check critical infrastructure satisfaction
        critical_types = {AgentType.POWER, AgentType.WATER}
        
        for agent in agents:
            if agent.agent_type in critical_types:
                satisfaction = allocation_status.get(agent.agent_type, 0.5)
                
                if satisfaction < 0.3:
                    risk_score += 0.3
                    warnings.append(
                        f"CRITICAL: {agent.agent_type.value} satisfaction at {satisfaction:.1%} - "
                        f"cascading failure risk!"
                    )
                elif satisfaction < 0.6:
                    risk_score += 0.15
                    warnings.append(
                        f"WARNING: {agent.agent_type.value} satisfaction at {satisfaction:.1%} - "
                        f"dependent services at risk"
                    )

        # Check dependent agents
        for agent in agents:
            dependencies = self.get_dependencies(agent.agent_type)
            if dependencies:
                dep_satisfaction = sum(
                    allocation_status.get(dep_type, 0.5) * impact
                    for dep_type, impact in dependencies
                ) / sum(impact for _, impact in dependencies)

                if dep_satisfaction < 0.4 and agent.agent_type == AgentType.HOSPITAL:
                    risk_score += 0.4
                    warnings.append(
                        f"CRITICAL: Hospital dependencies compromised - patient safety at risk!"
                    )

        risk_score = min(1.0, risk_score)
        return risk_score, warnings

    def get_priority_adjusted_agents(
        self,
        agents: List[Agent],
        allocation_status: Dict[AgentType, float],
    ) -> List[Tuple[Agent, float]]:
        """
        Return agents with priorities adjusted for dependencies.
        
        Returns:
            List of (agent, adjusted_priority) tuples
        """
        adjusted = []
        for agent in agents:
            adjusted_priority = self.adjust_priority_for_dependencies(agent, allocation_status)
            adjusted.append((agent, adjusted_priority))
        
        return adjusted
