"""MongoDB repositories for CrisisGrid data persistence"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database


class SimulationRepository:
    """Repository for simulation data persistence"""

    def __init__(self, db: Database):
        self.collection: Collection = db['simulations']

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        total_timesteps: int = 100,
    ) -> Dict[str, Any]:
        """Create a new simulation"""
        doc = {
            'name': name,
            'total_timesteps': total_timesteps,
            'current_timestep': 0,
            'is_running': False,
            'is_completed': False,
            'power_available': 1000.0,
            'water_available': 500.0,
            'stability_score': 1.0,
            'unmet_demand': 0.0,
            'risk_level': 0.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        if description is not None:
            doc['description'] = description
        result = self.collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    def get_by_id(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Get simulation by ID"""
        return self.collection.find_one({'_id': ObjectId(simulation_id)})

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all simulations with pagination"""
        return list(
            self.collection.find()
            .sort('created_at', -1)
            .skip(skip)
            .limit(limit)
        )

    def update_state(
        self,
        simulation_id: str,
        current_timestep: int = None,
        power_available: float = None,
        water_available: float = None,
        is_running: bool = None,
        is_completed: bool = None,
        stability_score: float = None,
        unmet_demand: float = None,
        risk_level: float = None,
    ) -> Optional[Dict[str, Any]]:
        """Update simulation state"""
        update_dict = {'updated_at': datetime.utcnow()}

        if current_timestep is not None:
            update_dict['current_timestep'] = current_timestep
        if power_available is not None:
            update_dict['power_available'] = power_available
        if water_available is not None:
            update_dict['water_available'] = water_available
        if is_running is not None:
            update_dict['is_running'] = is_running
        if is_completed is not None:
            update_dict['is_completed'] = is_completed
        if stability_score is not None:
            update_dict['stability_score'] = stability_score
        if unmet_demand is not None:
            update_dict['unmet_demand'] = unmet_demand
        if risk_level is not None:
            update_dict['risk_level'] = risk_level

        result = self.collection.find_one_and_update(
            {'_id': ObjectId(simulation_id)},
            {'$set': update_dict},
            return_document=True
        )
        return result

    def delete(self, simulation_id: str) -> bool:
        """Delete a simulation"""
        result = self.collection.delete_one({'_id': ObjectId(simulation_id)})
        return result.deleted_count > 0


class AgentRepository:
    """Repository for agent data persistence"""

    def __init__(self, db: Database):
        self.collection: Collection = db['agents']

    def create(
        self,
        simulation_id: str,
        agent_type: str,
        name: str,
        current_demand: float,
        max_demand: float,
        min_demand: float,
        priority_level: float,
        behavior_profile: str = "cooperative",
    ) -> Dict[str, Any]:
        """Create a new agent"""
        doc = {
            'simulation_id': ObjectId(simulation_id),
            'agent_type': agent_type,
            'name': name,
            'current_demand': current_demand,
            'allocated_resources': 0.0,
            'max_demand': max_demand,
            'min_demand': min_demand,
            'priority_level': priority_level,
            'dependency_factor': 1.0,
            'behavior_profile': behavior_profile,
            'risk_tolerance': 0.5,
            'cooperation_level': 0.5,
            'urgency_bias': 0.5,
            'trust_score': 0.5,
            'memory_log': [],
            'current_bid': 0.0,
            'unmet_demand': 0.0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        result = self.collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    def get_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        return self.collection.find_one({'_id': ObjectId(agent_id)})

    def get_by_simulation(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a simulation"""
        return list(
            self.collection.find({'simulation_id': ObjectId(simulation_id)})
        )

    def update_state(
        self,
        agent_id: str,
        current_demand: float = None,
        allocated_resources: float = None,
        unmet_demand: float = None,
        trust_score: float = None,
        current_bid: float = None,
    ) -> Optional[Dict[str, Any]]:
        """Update agent state"""
        update_dict = {'updated_at': datetime.utcnow()}

        if current_demand is not None:
            update_dict['current_demand'] = current_demand
        if allocated_resources is not None:
            update_dict['allocated_resources'] = allocated_resources
        if unmet_demand is not None:
            update_dict['unmet_demand'] = unmet_demand
        if trust_score is not None:
            update_dict['trust_score'] = trust_score
        if current_bid is not None:
            update_dict['current_bid'] = current_bid

        result = self.collection.find_one_and_update(
            {'_id': ObjectId(agent_id)},
            {'$set': update_dict},
            return_document=True
        )
        return result

    def update_memory(
        self,
        agent_id: str,
        memory_log: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Update agent memory log"""
        result = self.collection.find_one_and_update(
            {'_id': ObjectId(agent_id)},
            {'$set': {
                'memory_log': memory_log,
                'updated_at': datetime.utcnow()
            }},
            return_document=True
        )
        return result


class AllocationRepository:
    """Repository for allocation records"""

    def __init__(self, db: Database):
        self.collection: Collection = db['allocations']

    def create(
        self,
        simulation_id: str,
        agent_id: str,
        timestep: int,
        resource_type: str,
        allocated_amount: float,
        requested_amount: float,
        utility_score: float,
        was_fulfilled: float,
        explanation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create allocation record"""
        doc = {
            'simulation_id': ObjectId(simulation_id),
            'agent_id': ObjectId(agent_id),
            'timestep': timestep,
            'resource_type': resource_type,
            'allocated_amount': allocated_amount,
            'requested_amount': requested_amount,
            'utility_score': utility_score,
            'was_fulfilled': was_fulfilled,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        if explanation is not None:
            doc['explanation'] = explanation
        result = self.collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    def get_by_simulation(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Get all allocations for a simulation"""
        return list(
            self.collection.find({'simulation_id': ObjectId(simulation_id)})
            .sort('timestep', 1)
        )

    def get_by_timestep(
        self,
        simulation_id: str,
        timestep: int,
    ) -> List[Dict[str, Any]]:
        """Get allocations for a specific timestep"""
        return list(
            self.collection.find({
                'simulation_id': ObjectId(simulation_id),
                'timestep': timestep,
            })
        )

    def get_agent_allocation_history(
        self,
        simulation_id: str,
        agent_id: str,
    ) -> List[Dict[str, Any]]:
        """Get complete allocation history for an agent"""
        return list(
            self.collection.find({
                'simulation_id': ObjectId(simulation_id),
                'agent_id': ObjectId(agent_id),
            }).sort('timestep', 1)
        )


class EventRepository:
    """Repository for event records"""

    def __init__(self, db: Database):
        self.collection: Collection = db['events']

    def create(
        self,
        simulation_id: str,
        timestep: int,
        event_type: str,
        severity: float,
        affected_agent_type: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create event record"""
        doc = {
            'simulation_id': ObjectId(simulation_id),
            'timestep': timestep,
            'event_type': event_type,
            'severity': severity,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        if affected_agent_type is not None:
            doc['affected_agent_type'] = affected_agent_type
        if description is not None:
            doc['description'] = description
        result = self.collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    def get_by_simulation(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Get all events for a simulation"""
        return list(
            self.collection.find({'simulation_id': ObjectId(simulation_id)})
            .sort('timestep', 1)
        )

    def get_by_timestep(
        self,
        simulation_id: str,
        timestep: int,
    ) -> List[Dict[str, Any]]:
        """Get events for a specific timestep"""
        return list(
            self.collection.find({
                'simulation_id': ObjectId(simulation_id),
                'timestep': timestep,
            })
        )


class TimestepLogRepository:
    """Repository for timestep logs"""

    def __init__(self, db: Database):
        self.collection: Collection = db['timestep_logs']

    def create(
        self,
        simulation_id: str,
        timestep: int,
        power_available: float,
        water_available: float,
        power_allocated: float,
        water_allocated: float,
        stability_score: float,
        risk_level: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a timestep log record"""
        events_summary = kwargs.get('events_summary', [])
        if events_summary is None:
            events_summary = []
        doc = {
            'simulation_id': ObjectId(simulation_id),
            'timestep': timestep,
            'power_available': power_available,
            'water_available': water_available,
            'power_allocated': power_allocated,
            'water_allocated': water_allocated,
            'stability_score': stability_score,
            'risk_level': risk_level,
            'unmet_demand': kwargs.get('unmet_demand', 0.0),
            'allocation_efficiency': kwargs.get('allocation_efficiency', 0.0),
            'fairness_score': kwargs.get('fairness_score', 0.0),
            'total_agents': kwargs.get('total_agents', 0),
            'agents_satisfied': kwargs.get('agents_satisfied', 0),
            'agents_critical': kwargs.get('agents_critical', 0),
            'events_occurred': kwargs.get('events_occurred', 0),
            'events_summary': events_summary,
            'total_bids': kwargs.get('total_bids', 0),
            'avg_utility_score': kwargs.get('avg_utility_score', 0.0),
            'highest_utility_score': kwargs.get('highest_utility_score', 0.0),
            'avg_trust_score': kwargs.get('avg_trust_score', 0.5),
            'min_trust_score': kwargs.get('min_trust_score', 0.5),
            'max_trust_score': kwargs.get('max_trust_score', 0.5),
            'power_satisfaction_rate': kwargs.get('power_satisfaction_rate', 0.0),
            'water_satisfaction_rate': kwargs.get('water_satisfaction_rate', 0.0),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        notes = kwargs.get('notes', None)
        if notes is not None:
            doc['notes'] = notes
        result = self.collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    def get_by_simulation(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Get all timestep logs for a simulation"""
        return list(
            self.collection.find({'simulation_id': ObjectId(simulation_id)})
            .sort('timestep', 1)
        )

    def get_by_timestep(
        self,
        simulation_id: str,
        timestep: int,
    ) -> Optional[Dict[str, Any]]:
        """Get timestep log for specific timestep"""
        return self.collection.find_one({
            'simulation_id': ObjectId(simulation_id),
            'timestep': timestep,
        })

    def get_range(
        self,
        simulation_id: str,
        start_timestep: int,
        end_timestep: int,
    ) -> List[Dict[str, Any]]:
        """Get timestep logs for a range of timesteps"""
        return list(
            self.collection.find({
                'simulation_id': ObjectId(simulation_id),
                'timestep': {'$gte': start_timestep, '$lte': end_timestep},
            }).sort('timestep', 1)
        )


class SystemStateRepository:
    """Repository for current system state (real-time queries)"""

    def __init__(self, db: Database):
        self.collection: Collection = db['system_state']

    def upsert(
        self,
        simulation_id: str,
        total_power: float,
        total_water: float,
        power_allocated: float,
        water_allocated: float,
        active_agents: int,
        critical_agents: int,
        stability: float,
        risk: float,
        unmet_demand: float,
        active_events: List[Dict] = None,
    ) -> Dict[str, Any]:
        """Create or update system state (one per simulation)"""
        if active_events is None:
            active_events = []

        doc = {
            'simulation_id': ObjectId(simulation_id),
            'total_power': total_power,
            'total_water': total_water,
            'power_allocated': power_allocated,
            'water_allocated': water_allocated,
            'active_agents': active_agents,
            'critical_agents': critical_agents,
            'stability': stability,
            'risk': risk,
            'unmet_demand': unmet_demand,
            'active_events': active_events,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }

        result = self.collection.find_one_and_update(
            {'simulation_id': ObjectId(simulation_id)},
            {'$set': doc},
            upsert=True,
            return_document=True
        )
        return result

    def get_by_simulation(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Get current system state for a simulation"""
        return self.collection.find_one({'simulation_id': ObjectId(simulation_id)})

    def delete_by_simulation(self, simulation_id: str) -> bool:
        """Delete system state for a simulation"""
        result = self.collection.delete_one({'simulation_id': ObjectId(simulation_id)})
        return result.deleted_count > 0
