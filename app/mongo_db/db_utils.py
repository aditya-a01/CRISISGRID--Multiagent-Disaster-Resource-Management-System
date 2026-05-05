"""MongoDB utilities for transactions, consistency, and optimization"""

from typing import Optional, Callable, Any, Dict
from bson.objectid import ObjectId
from pymongo.client_session import ClientSession
from pymongo.database import Database
import logging

logger = logging.getLogger(__name__)


class MongoDBTransactionManager:
    """Manages MongoDB transactions for atomic multi-document operations"""

    def __init__(self, client, db: Database):
        self.client = client
        self.db = db

    def execute_atomic_timestep_update(
        self,
        simulation_id: str,
        timestep: int,
        update_fn: Callable[[Database], bool],
    ) -> bool:
        """
        Execute timestep update atomically using MongoDB transactions.
        
        All updates (simulation state, agent state, allocations, logs) must succeed together.
        If any step fails, entire transaction rolls back.
        
        Args:
            simulation_id: Simulation ID
            timestep: Timestep number
            update_fn: Function that performs updates, returns True on success
            
        Returns:
            True if transaction committed, False if rolled back
        """
        session = self.client.start_session()

        try:
            with session.start_transaction():
                # Execute update function within transaction
                success = update_fn(self.db)

                if success:
                    logger.info(f"✓ Atomic update successful: sim={simulation_id}, step={timestep}")
                    return True
                else:
                    logger.error(f"✗ Update function failed: sim={simulation_id}, step={timestep}")
                    session.abort_transaction()
                    return False

        except Exception as e:
            logger.error(f"✗ Transaction error: {str(e)}")
            session.abort_transaction()
            return False

        finally:
            session.end_session()

    def execute_safe_deletion(self, simulation_id: str) -> bool:
        """
        Safely delete a simulation and all related data.
        
        Deletion order:
        1. Allocations
        2. Events
        3. Timestep Logs
        4. System State
        5. Agents
        6. Simulation
        
        Args:
            simulation_id: Simulation ID to delete
            
        Returns:
            True if deletion succeeded, False otherwise
        """
        session = self.client.start_session()

        try:
            with session.start_transaction():
                sim_id = ObjectId(simulation_id)

                # Delete in correct order to respect relationships
                allocations_deleted = self.db['allocations'].delete_many(
                    {'simulation_id': sim_id}
                )

                events_deleted = self.db['events'].delete_many(
                    {'simulation_id': sim_id}
                )

                logs_deleted = self.db['timestep_logs'].delete_many(
                    {'simulation_id': sim_id}
                )

                state_deleted = self.db['system_state'].delete_many(
                    {'simulation_id': sim_id}
                )

                agents_deleted = self.db['agents'].delete_many(
                    {'simulation_id': sim_id}
                )

                sim_deleted = self.db['simulations'].delete_many(
                    {'_id': sim_id}
                )

                logger.info(
                    f"✓ Safe deletion complete: sim={simulation_id} "
                    f"(allocations={allocations_deleted.deleted_count}, "
                    f"events={events_deleted.deleted_count}, "
                    f"logs={logs_deleted.deleted_count}, "
                    f"agents={agents_deleted.deleted_count}, "
                    f"sim={sim_deleted.deleted_count})"
                )
                return True

        except Exception as e:
            logger.error(f"✗ Safe deletion failed: {str(e)}")
            return False

        finally:
            session.end_session()


class MongoDBConsistencyValidator:
    """Validates MongoDB data consistency and detects anomalies"""

    def __init__(self, db: Database):
        self.db = db

    def validate_simulation_state(self, simulation_id: str) -> Dict[str, Any]:
        """
        Validate simulation data consistency.
        
        Checks:
        - All agents belong to this simulation
        - All allocations reference existing agents
        - All events belong to this simulation
        - Metrics are within valid ranges
        """
        issues = []
        warnings = []

        try:
            sim_id = ObjectId(simulation_id)
            sim = self.db['simulations'].find_one({'_id': sim_id})

            if not sim:
                return {'valid': False, 'error': 'Simulation not found'}

            # Check agents
            agents = list(self.db['agents'].find({'simulation_id': sim_id}))
            if not agents:
                warnings.append('No agents found for simulation')

            # Check allocations
            allocations = list(
                self.db['allocations'].find({'simulation_id': sim_id})
            )

            for alloc in allocations:
                agent = self.db['agents'].find_one({'_id': alloc['agent_id']})
                if not agent:
                    issues.append(
                        f"Allocation {alloc['_id']} references non-existent agent {alloc['agent_id']}"
                    )
                elif agent['simulation_id'] != sim_id:
                    issues.append(
                        f"Allocation {alloc['_id']} agent {alloc['agent_id']} "
                        f"belongs to different simulation"
                    )

            # Check metrics ranges
            if not (0.0 <= sim.get('stability_score', 0) <= 1.0):
                issues.append(f"Simulation stability_score out of range: {sim['stability_score']}")
            if not (0.0 <= sim.get('risk_level', 0) <= 1.0):
                issues.append(f"Simulation risk_level out of range: {sim['risk_level']}")
            if sim.get('unmet_demand', 0) < 0.0:
                issues.append(f"Simulation unmet_demand negative: {sim['unmet_demand']}")

            # Check agent metrics
            for agent in agents:
                if not (0.0 <= agent.get('trust_score', 0.5) <= 1.0):
                    issues.append(f"Agent {agent['_id']} trust_score out of range")
                if agent.get('allocated_resources', 0) < 0.0:
                    issues.append(f"Agent {agent['_id']} allocated_resources negative")
                if agent.get('unmet_demand', 0) < 0.0:
                    issues.append(f"Agent {agent['_id']} unmet_demand negative")

            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'agent_count': len(agents),
                'allocation_count': len(allocations),
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
            }

    def detect_data_anomalies(self, simulation_id: str) -> Dict[str, Any]:
        """
        Detect unusual patterns that might indicate data issues.
        
        Checks:
        - Missing timestep logs
        - Extreme stability drops
        - Resource over-allocation
        """
        anomalies = []

        try:
            sim_id = ObjectId(simulation_id)
            logs = list(
                self.db['timestep_logs'].find(
                    {'simulation_id': sim_id}
                ).sort('timestep', 1)
            )

            # Check for missing timesteps
            if logs:
                expected_steps = logs[-1]['timestep'] + 1
                if len(logs) != expected_steps:
                    anomalies.append(
                        f"Missing timestep logs: expected {expected_steps}, got {len(logs)}"
                    )

                # Check for extreme stability drops
                for i in range(1, len(logs)):
                    drop = logs[i - 1].get('stability_score', 0) - logs[i].get('stability_score', 0)
                    if drop > 0.5:
                        anomalies.append(
                            f"Extreme stability drop at step {logs[i]['timestep']}: "
                            f"{logs[i-1].get('stability_score'):.2f} → "
                            f"{logs[i].get('stability_score'):.2f}"
                        )

                # Check for resource over-allocation
                for log in logs:
                    power_available = log.get('power_available', 0)
                    power_allocated = log.get('power_allocated', 0)
                    if power_allocated > power_available * 1.01:  # Allow 1% rounding
                        anomalies.append(
                            f"Power over-allocated at step {log['timestep']}: "
                            f"available={power_available}, allocated={power_allocated}"
                        )

            return {
                'has_anomalies': len(anomalies) > 0,
                'anomalies': anomalies,
                'timestep_logs_count': len(logs),
            }

        except Exception as e:
            return {
                'has_anomalies': True,
                'error': str(e),
            }

    def check_cascade_relationships(self, simulation_id: str) -> Dict[str, Any]:
        """
        Verify relationships and detect orphaned records.
        """
        issues = []

        try:
            sim_id = ObjectId(simulation_id)

            # Check agents belong to simulation
            agents = list(self.db['agents'].find({'simulation_id': sim_id}))
            for agent in agents:
                sim = self.db['simulations'].find_one({'_id': agent['simulation_id']})
                if not sim:
                    issues.append(f"Agent {agent['_id']} references non-existent simulation")

            # Check allocations reference existing agents and simulations
            allocations = list(
                self.db['allocations'].find({'simulation_id': sim_id})
            )
            for alloc in allocations:
                agent = self.db['agents'].find_one({'_id': alloc['agent_id']})
                if not agent:
                    issues.append(f"Allocation {alloc['_id']} references non-existent agent")

            # Check events belong to simulation
            events = list(self.db['events'].find({'simulation_id': sim_id}))
            for evt in events:
                sim = self.db['simulations'].find_one({'_id': evt['simulation_id']})
                if not sim:
                    issues.append(f"Event {evt['_id']} references non-existent simulation")

            return {
                'valid': len(issues) == 0,
                'issues': issues,
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
            }


class MongoDBOptimizer:
    """Tools for MongoDB performance analysis and optimization"""

    def __init__(self, db: Database):
        self.db = db

    def analyze_query_performance(self) -> Dict[str, int]:
        """Get collection statistics"""
        stats = {}

        collections = [
            'simulations', 'agents', 'allocations', 'events',
            'timestep_logs', 'system_state'
        ]

        for collection_name in collections:
            try:
                count = self.db[collection_name].count_documents({})
                stats[collection_name] = count
            except Exception as e:
                logger.warning(f"Failed to count {collection_name}: {e}")
                stats[collection_name] = 0

        return stats

    def get_index_information(self) -> Dict[str, list]:
        """Get information about indexes on all collections"""
        index_info = {
            'simulations': [
                'idx_created_at',
                'idx_is_completed',
            ],
            'agents': [
                'idx_simulation_id',
                'idx_trust_score',
                'idx_sim_type',
            ],
            'allocations': [
                'idx_sim_timestep',
                'idx_agent_resource',
                'idx_resource_type',
            ],
            'events': [
                'idx_sim_timestep',
                'idx_event_type',
            ],
            'timestep_logs': [
                'idx_sim_timestep',
                'idx_created_at',
            ],
            'system_state': [
                'idx_simulation_id',
                'idx_updated_at',
            ],
        }

        return index_info

    def suggest_optimizations(self) -> list:
        """Suggest optimizations based on schema"""
        suggestions = [
            'Use TimestepLog for aggregate queries instead of summing allocations',
            'Archive old simulations to separate database for historical analysis',
            'Consider partitioning allocations by simulation_id for large datasets',
            'Add TTL index on event logs for automatic cleanup',
            'Cache frequently accessed simulations in application layer',
            'Use MongoDB Atlas for automatic backups and replication',
            'Monitor query performance using MongoDB Profiler',
            'Consider sharding by simulation_id for horizontal scaling',
        ]

        return suggestions

    def estimate_storage_usage(self) -> Dict[str, str]:
        """Estimate database storage by collection"""
        return {
            'note': 'Estimates based on typical document sizes',
            'avg_simulation_doc_bytes': 500,
            'avg_agent_doc_bytes': 2000,
            'avg_allocation_doc_bytes': 300,
            'avg_event_doc_bytes': 400,
            'avg_timestep_log_doc_bytes': 5000,
            'avg_system_state_doc_bytes': 1500,
        }
