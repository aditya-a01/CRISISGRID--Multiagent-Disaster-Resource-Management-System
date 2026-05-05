"""Core agent implementation with behavioral AI"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import math


class AgentType(str, Enum):
    """Types of agents in crisis response"""
    HOSPITAL = "hospital"
    WATER = "water"
    POWER = "power"
    EMERGENCY = "emergency"


class BehaviorProfile(str, Enum):
    """Behavior profiles for decision-making"""
    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    ADAPTIVE = "adaptive"


@dataclass
class MemoryEntry:
    """Single entry in agent memory log"""
    timestep: int
    event: str
    reward: float  # Positive = favorable, negative = unfavorable


@dataclass
class Agent:
    """Core autonomous agent with behavioral AI"""

    # Identity
    agent_id: int
    agent_type: AgentType
    name: str

    # Demand and resources
    current_demand: float
    max_demand: float
    min_demand: float
    allocated_resources: float = 0.0
    current_bid: float = 0.0

    # Priority system
    priority_level: float = 1.0  # Base priority (0.0 to 2.0+)
    dependency_factor: float = 1.0  # How dependent on other resources

    # Behavioral characteristics
    behavior_profile: BehaviorProfile = BehaviorProfile.ADAPTIVE
    risk_tolerance: float = 0.5  # 0.0 (risk-averse) to 1.0 (risk-seeking)
    cooperation_level: float = 0.5  # 0.0 (competitive) to 1.0 (cooperative)
    urgency_bias: float = 0.5  # 0.0 (patient) to 1.0 (urgent)

    # Trust system
    trust_score: float = 0.5  # 0.0 to 1.0
    memory_log: List[MemoryEntry] = field(default_factory=list)

    # State tracking
    unmet_demand: float = 0.0
    satisfaction_history: List[float] = field(default_factory=list)

    def calculate_utility(
        self,
        impact_score: float = 1.0,
        available_resources: float = 100.0,
    ) -> float:
        """
        Calculate utility for bidding:
        Utility = (priority × demand × impact × dependency_factor) × behavior_factor × trust_score
        """
        base_utility = (
            self.priority_level
            * self.current_demand
            * impact_score
            * self.dependency_factor
        )

        # Behavioral modifier based on profile and characteristics
        behavior_factor = self._calculate_behavior_factor(available_resources)

        # Final utility
        utility = base_utility * behavior_factor * self.trust_score
        return max(0.0, utility)

    def _calculate_behavior_factor(self, available_resources: float) -> float:
        """Calculate behavioral modifier based on profile and traits"""
        if self.behavior_profile == BehaviorProfile.COOPERATIVE:
            # Cooperative agents moderate their demands
            return 0.8 + (self.cooperation_level * 0.2)

        elif self.behavior_profile == BehaviorProfile.COMPETITIVE:
            # Competitive agents amplify their demands
            return 1.2 + (self.risk_tolerance * 0.3)

        elif self.behavior_profile == BehaviorProfile.ADAPTIVE:
            # Adaptive agents adjust based on scarcity
            scarcity_ratio = 1.0 - (available_resources / 1000.0)  # Assumes ~1000 typical total
            scarcity_ratio = max(0.0, min(1.0, scarcity_ratio))

            if scarcity_ratio > 0.7:
                # High scarcity: cooperative agents cooperate, competitive agents push
                return 0.9 + (self.cooperation_level * 0.2)
            else:
                # Low scarcity: more balanced
                return 1.0
        
        return 1.0

    def submit_bid(self) -> float:
        """Submit a bid for resources based on current utility"""
        self.current_bid = self.calculate_utility()
        return self.current_bid

    def receive_allocation(self, allocated: float, timestep: int):
        """Process resource allocation and update satisfaction"""
        self.allocated_resources = allocated
        self.unmet_demand = max(0.0, self.current_demand - allocated)

        # Record satisfaction
        satisfaction = (allocated / self.current_demand) if self.current_demand > 0 else 1.0
        satisfaction = min(1.0, satisfaction)
        self.satisfaction_history.append(satisfaction)

        # Update memory
        reward = satisfaction - 0.5  # Positive if satisfaction > 0.5
        self.memory_log.append(
            MemoryEntry(
                timestep=timestep,
                event=f"allocated {allocated:.2f}/{self.current_demand:.2f}",
                reward=reward,
            )
        )

    def update_trust_score(self, fairness_metric: float, cooperation_metric: float):
        """
        Update trust score based on fairness and past cooperation.
        
        Args:
            fairness_metric: 0.0 (unfair) to 1.0 (fair allocation)
            cooperation_metric: 0.0 (uncooperative) to 1.0 (highly cooperative)
        """
        # Weighted average: 60% fairness, 40% past cooperation
        new_trust = (fairness_metric * 0.6) + (cooperation_metric * 0.4)

        # Smooth transition to new trust value
        self.trust_score = 0.7 * self.trust_score + 0.3 * new_trust
        self.trust_score = max(0.0, min(1.0, self.trust_score))

    def update_demand(self, new_demand: float, timestep: int):
        """Update current demand, respecting min/max bounds"""
        old_demand = self.current_demand
        self.current_demand = max(self.min_demand, min(self.max_demand, new_demand))

        if self.current_demand != old_demand:
            self.memory_log.append(
                MemoryEntry(
                    timestep=timestep,
                    event=f"demand changed: {old_demand:.2f} -> {self.current_demand:.2f}",
                    reward=0.0,
                )
            )

    def adjust_behavior(self, timestep: int):
        """Adaptive behavior adjustment based on recent history"""
        if len(self.satisfaction_history) < 3:
            return

        # Check recent satisfaction trend (last 3 timesteps)
        recent_satisfaction = sum(self.satisfaction_history[-3:]) / 3
        
        if recent_satisfaction < 0.3:
            # Consistently unmet: increase urgency and risk tolerance
            self.urgency_bias = min(1.0, self.urgency_bias + 0.1)
            self.risk_tolerance = min(1.0, self.risk_tolerance + 0.05)
            self.memory_log.append(
                MemoryEntry(timestep=timestep, event="increased urgency due to low satisfaction", reward=-0.5)
            )
        elif recent_satisfaction > 0.8:
            # Consistently met: decrease urgency, increase cooperation
            self.urgency_bias = max(0.0, self.urgency_bias - 0.05)
            self.cooperation_level = min(1.0, self.cooperation_level + 0.05)
            self.memory_log.append(
                MemoryEntry(timestep=timestep, event="decreased urgency due to high satisfaction", reward=0.5)
            )

    def get_state(self) -> Dict:
        """Return current state snapshot"""
        return {
            "id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type.value,
            "current_demand": self.current_demand,
            "allocated_resources": self.allocated_resources,
            "current_bid": self.current_bid,
            "unmet_demand": self.unmet_demand,
            "trust_score": self.trust_score,
            "priority_level": self.priority_level,
            "risk_tolerance": self.risk_tolerance,
            "cooperation_level": self.cooperation_level,
            "behavior_profile": self.behavior_profile.value,
        }

    def __repr__(self):
        return (
            f"<Agent {self.name} (type={self.agent_type.value}) "
            f"demand={self.current_demand:.1f} "
            f"allocated={self.allocated_resources:.1f} "
            f"trust={self.trust_score:.2f}>"
        )
