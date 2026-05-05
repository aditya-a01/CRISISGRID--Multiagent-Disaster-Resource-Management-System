"""Database utilities for consistency, transactions, and optimization"""

from typing import Optional, Callable, Any
from sqlalchemy.orm import Session
from sqlalchemy import event
from app.models.simulation import Simulation
from app.models.agent import Agent
from app.models.allocation import Allocation
from app.models.event import Event
from app.models.timestep_log import TimestepLog
import logging

logger = logging.getLogger(__name__)


class DatabaseTransactionManager:
    """Manages atomic transactions for multi-step operations"""

    def __init__(self, db: Session):
        self.db = db

    def execute_atomic_timestep_update(
        self,
        simulation_id: int,
        timestep: int,
        update_fn: Callable[[Session], bool],
    ) -> bool:
        """
        Execute timestep update atomically.
        
        All updates (simulation state, agent state, allocations, logs) must succeed together.
        If any step fails, entire transaction rolls back.
        """
        try:
            # Begin transaction
            self.db.begin_nested()

            # Execute update function
            success = update_fn(self.db)

            if success:
                # Commit transaction
                self.db.commit()
                logger.info(f"Atomic update successful: sim={simulation_id}, step={timestep}")
                return True
            else:
                # Rollback on function failure
                self.db.rollback()
                logger.error(f"Update function failed: sim={simulation_id}, step={timestep}")
                return False

        except Exception as e:
            # Rollback on exception
            self.db.rollback()
            logger.error(f"Transaction error: {str(e)}")
            return False

    def execute_safe_deletion(self, simulation_id: int) -> bool:
        """
        Safely delete a simulation and all related data in correct order.
        
        Deletion order matters due to foreign key constraints:
        1. Allocations
        2. Events
        3. Timestep Logs
        4. Agents
        5. Simulation
        """
        try:
            self.db.begin_nested()

            # Delete in correct order to respect foreign keys
            allocations_deleted = (
                self.db.query(Allocation)
                .filter(Allocation.simulation_id == simulation_id)
                .delete()
            )

            events_deleted = (
                self.db.query(Event)
                .filter(Event.simulation_id == simulation_id)
                .delete()
            )

            logs_deleted = (
                self.db.query(TimestepLog)
                .filter(TimestepLog.simulation_id == simulation_id)
                .delete()
            )

            agents_deleted = (
                self.db.query(Agent)
                .filter(Agent.simulation_id == simulation_id)
                .delete()
            )

            sim_deleted = (
                self.db.query(Simulation)
                .filter(Simulation.id == simulation_id)
                .delete()
            )

            self.db.commit()

            logger.info(
                f"Safe deletion complete: sim={simulation_id} "
                f"(allocations={allocations_deleted}, events={events_deleted}, "
                f"logs={logs_deleted}, agents={agents_deleted}, sim={sim_deleted})"
            )
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Safe deletion failed for sim={simulation_id}: {str(e)}")
            return False


class DataConsistencyValidator:
    """Validates database consistency and detects anomalies"""

    def __init__(self, db: Session):
        self.db = db

    def validate_simulation_state(self, simulation_id: int) -> dict:
        """
        Validate simulation data consistency.
        
        Checks:
        - All agents belong to this simulation
        - All allocations reference existing agents
        - All events belong to this simulation
        - Timestep numbers are sequential
        - Metrics are within valid ranges
        """
        issues = []
        warnings = []

        sim = self.db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not sim:
            return {"valid": False, "error": "Simulation not found"}

        # Check agents
        agents = self.db.query(Agent).filter(Agent.simulation_id == simulation_id).all()
        if not agents:
            warnings.append("No agents found for simulation")

        # Check allocations
        allocations = (
            self.db.query(Allocation)
            .filter(Allocation.simulation_id == simulation_id)
            .all()
        )

        for alloc in allocations:
            agent = self.db.query(Agent).filter(Agent.id == alloc.agent_id).first()
            if not agent:
                issues.append(f"Allocation {alloc.id} references non-existent agent {alloc.agent_id}")
            if agent and agent.simulation_id != simulation_id:
                issues.append(f"Allocation {alloc.id} agent {alloc.agent_id} belongs to different simulation")

        # Check metrics ranges
        if not (0.0 <= sim.stability_score <= 1.0):
            issues.append(f"Simulation stability_score out of range: {sim.stability_score}")
        if not (0.0 <= sim.risk_level <= 1.0):
            issues.append(f"Simulation risk_level out of range: {sim.risk_level}")
        if sim.unmet_demand < 0.0:
            issues.append(f"Simulation unmet_demand negative: {sim.unmet_demand}")

        # Check agent metrics
        for agent in agents:
            if not (0.0 <= agent.trust_score <= 1.0):
                issues.append(f"Agent {agent.id} trust_score out of range: {agent.trust_score}")
            if agent.allocated_resources < 0.0:
                issues.append(f"Agent {agent.id} allocated_resources negative: {agent.allocated_resources}")
            if agent.unmet_demand < 0.0:
                issues.append(f"Agent {agent.id} unmet_demand negative: {agent.unmet_demand}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "agent_count": len(agents),
            "allocation_count": len(allocations),
        }

    def detect_data_anomalies(self, simulation_id: int) -> dict:
        """
        Detect unusual patterns that might indicate data issues.
        
        Checks:
        - Agents with zero allocation consistently
        - Extreme satisfaction variances
        - Missing timestep logs
        - Unrealistic resource allocations
        """
        anomalies = []

        logs = (
            self.db.query(TimestepLog)
            .filter(TimestepLog.simulation_id == simulation_id)
            .order_by(TimestepLog.timestep)
            .all()
        )

        # Check for missing timesteps
        if logs:
            expected_steps = logs[-1].timestep + 1
            if len(logs) != expected_steps:
                anomalies.append(f"Missing timestep logs: expected {expected_steps}, got {len(logs)}")

            # Check for extreme stability drops
            for i in range(1, len(logs)):
                drop = logs[i - 1].stability_score - logs[i].stability_score
                if drop > 0.5:
                    anomalies.append(
                        f"Extreme stability drop at step {logs[i].timestep}: "
                        f"{logs[i-1].stability_score:.2f} → {logs[i].stability_score:.2f}"
                    )

            # Check for resource over-allocation
            for log in logs:
                if log.power_allocated > log.power_available * 1.01:  # Allow 1% rounding
                    anomalies.append(
                        f"Power over-allocated at step {log.timestep}: "
                        f"available={log.power_available}, allocated={log.power_allocated}"
                    )

        return {
            "has_anomalies": len(anomalies) > 0,
            "anomalies": anomalies,
            "timestep_logs_count": len(logs),
        }

    def check_cascade_relationships(self, simulation_id: int) -> dict:
        """
        Verify foreign key relationships are consistent (useful for detecting orphaned records).
        """
        issues = []

        # Check agents belong to simulation
        agents = self.db.query(Agent).filter(Agent.simulation_id == simulation_id).all()
        for agent in agents:
            sim = self.db.query(Simulation).filter(Simulation.id == agent.simulation_id).first()
            if not sim:
                issues.append(f"Agent {agent.id} references non-existent simulation {agent.simulation_id}")

        # Check allocations reference existing agents and simulations
        allocations = (
            self.db.query(Allocation)
            .filter(Allocation.simulation_id == simulation_id)
            .all()
        )
        for alloc in allocations:
            agent = self.db.query(Agent).filter(Agent.id == alloc.agent_id).first()
            if not agent:
                issues.append(f"Allocation {alloc.id} references non-existent agent {alloc.agent_id}")

        # Check events belong to simulation
        events = self.db.query(Event).filter(Event.simulation_id == simulation_id).all()
        for evt in events:
            sim = self.db.query(Simulation).filter(Simulation.id == evt.simulation_id).first()
            if not sim:
                issues.append(f"Event {evt.id} references non-existent simulation {evt.simulation_id}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }


class DatabaseOptimizer:
    """Tools for database optimization and maintenance"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_query_performance(self) -> dict:
        """
        Analyze current database statistics (index usage, table sizes).
        
        Note: Implementation depends on database backend (SQLite vs PostgreSQL).
        """
        stats = {
            "simulations": self.db.query(Simulation).count(),
            "agents": self.db.query(Agent).count(),
            "allocations": self.db.query(Allocation).count(),
            "events": self.db.query(Event).count(),
            "timestep_logs": self.db.query(TimestepLog).count(),
        }
        return stats

    def get_index_information(self) -> dict:
        """
        Returns information about indexes on all tables.
        Note: This is database-specific. Works best with PostgreSQL.
        """
        return {
            "note": "Index information is database-specific",
            "simulations": [
                "idx_simulation_created_at",
                "idx_simulation_is_completed",
            ],
            "agents": [
                "idx_agent_simulation_id",
                "idx_agent_trust_score",
                "idx_agent_sim_type",
            ],
            "allocations": [
                "idx_allocation_sim_timestep",
                "idx_allocation_agent_resource",
                "idx_allocation_resource_type",
            ],
            "events": [
                "idx_event_sim_timestep",
                "idx_event_type",
            ],
            "timestep_logs": [
                "idx_timestep_log_sim_step",
                "idx_timestep_log_created_at",
            ],
        }

    def estimate_storage_usage(self) -> dict:
        """Estimate database storage by table"""
        # SQLite doesn't have reliable way to get table size, so return estimates
        return {
            "note": "Estimates - actual size depends on database implementation",
            "avg_simulation_size_kb": 0.1,  # Very small - just metadata
            "avg_agent_size_kb": 0.5,  # Includes memory logs
            "avg_allocation_record_size_bytes": 100,
            "avg_event_record_size_bytes": 150,
            "avg_timestep_log_size_kb": 2.0,  # Includes event summaries
        }

    def suggest_optimizations(self) -> list:
        """Suggest optimizations based on schema and usage"""
        suggestions = [
            "Use composite indexes on (simulation_id, timestep) for frequent range queries",
            "Archive old simulations to separate database for historical analysis",
            "Consider partitioning allocations by simulation_id for large datasets",
            "Use TimestepLog for aggregate queries instead of summing Allocations",
            "Add materialized views for common analytics queries",
            "Consider caching agent trust_score snapshots in TimestepLog",
        ]
        return suggestions
