"""MongoDB analytics repository for historical queries and performance analysis"""

from typing import List, Dict, Any, Tuple
from datetime import datetime
from bson.objectid import ObjectId
from pymongo.database import Database


class AnalyticsRepository:
    """Advanced queries for historical analysis and performance metrics"""

    def __init__(self, db: Database):
        self.db = db

    def get_agent_allocation_history(
        self,
        simulation_id: str,
        agent_id: str,
    ) -> List[Dict[str, Any]]:
        """Get complete allocation history for an agent"""
        allocations = list(
            self.db['allocations'].find({
                'simulation_id': ObjectId(simulation_id),
                'agent_id': ObjectId(agent_id),
            }).sort('timestep', 1)
        )

        return [
            {
                'timestep': a['timestep'],
                'resource': a['resource_type'],
                'requested': a['requested_amount'],
                'allocated': a['allocated_amount'],
                'fulfilled': a['was_fulfilled'],
                'utility': a['utility_score'],
            }
            for a in allocations
        ]

    def get_agent_satisfaction_trend(
        self,
        simulation_id: str,
        agent_id: str,
    ) -> List[Tuple[int, float]]:
        """Get satisfaction trend for agent (timestep, satisfaction_rate)"""
        allocations = list(
            self.db['allocations'].find({
                'simulation_id': ObjectId(simulation_id),
                'agent_id': ObjectId(agent_id),
            }).sort('timestep', 1)
        )

        return [(a['timestep'], a['was_fulfilled']) for a in allocations]

    def get_resource_efficiency_by_type(
        self,
        simulation_id: str,
    ) -> Dict[str, Dict[str, float]]:
        """Get allocation efficiency metrics by resource type"""
        pipeline = [
            {'$match': {'simulation_id': ObjectId(simulation_id)}},
            {
                '$group': {
                    '_id': '$resource_type',
                    'total_allocated': {'$sum': '$allocated_amount'},
                    'total_requested': {'$sum': '$requested_amount'},
                    'avg_fulfillment': {'$avg': '$was_fulfilled'},
                }
            }
        ]

        results = list(self.db['allocations'].aggregate(pipeline))

        efficiency = {}
        for result in results:
            resource = result['_id']
            efficiency[resource] = {
                'total_allocated': float(result.get('total_allocated', 0)),
                'total_requested': float(result.get('total_requested', 0)),
                'efficiency': float(result.get('avg_fulfillment', 0)),
            }

        return efficiency

    def get_agent_trust_evolution(
        self,
        simulation_id: str,
        agent_id: str,
    ) -> List[Dict[str, Any]]:
        """Get trust score evolution for an agent"""
        agent = self.db['agents'].find_one({
            '_id': ObjectId(agent_id),
            'simulation_id': ObjectId(simulation_id),
        })

        if agent:
            return [{'current_trust': float(agent.get('trust_score', 0.5))}]
        return []

    def get_fairness_metrics(self, simulation_id: str) -> Dict[str, float]:
        """Get fairness metrics for entire simulation"""
        logs = list(
            self.db['timestep_logs'].find({
                'simulation_id': ObjectId(simulation_id)
            })
        )

        if not logs:
            return {
                'avg_fairness': 0.0,
                'min_fairness': 0.0,
                'max_fairness': 0.0,
            }

        fairness_scores = [log.get('fairness_score', 0) for log in logs]

        return {
            'avg_fairness': sum(fairness_scores) / len(fairness_scores),
            'min_fairness': min(fairness_scores),
            'max_fairness': max(fairness_scores),
        }

    def get_event_impact_analysis(self, simulation_id: str) -> Dict[str, Any]:
        """Analyze impact of events on system stability"""
        events = list(
            self.db['events'].find({
                'simulation_id': ObjectId(simulation_id)
            }).sort('timestep', 1)
        )

        logs = list(
            self.db['timestep_logs'].find({
                'simulation_id': ObjectId(simulation_id)
            })
        )

        event_impacts = {}

        for event in events:
            event_type = event.get('event_type', 'unknown')

            if event_type not in event_impacts:
                event_impacts[event_type] = {
                    'count': 0,
                    'total_severity': 0.0,
                    'avg_risk_after': 0.0,
                }

            # Find corresponding log
            matching_log = next(
                (log for log in logs if log.get('timestep') == event.get('timestep')),
                None
            )

            event_impacts[event_type]['count'] += 1
            event_impacts[event_type]['total_severity'] += event.get('severity', 0)
            if matching_log:
                event_impacts[event_type]['avg_risk_after'] += matching_log.get('risk_level', 0)

        # Calculate averages
        for event_type in event_impacts:
            count = event_impacts[event_type]['count']
            event_impacts[event_type]['avg_severity'] = event_impacts[event_type]['total_severity'] / count
            event_impacts[event_type]['avg_risk_after'] /= count

        return event_impacts

    def get_stability_trend(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Get stability score trend across all timesteps"""
        logs = list(
            self.db['timestep_logs'].find({
                'simulation_id': ObjectId(simulation_id)
            }).sort('timestep', 1)
        )

        return [
            {
                'timestep': log['timestep'],
                'stability': float(log.get('stability_score', 0)),
                'risk': float(log.get('risk_level', 0)),
                'unmet_demand': float(log.get('unmet_demand', 0)),
            }
            for log in logs
        ]

    def get_critical_agents_timeline(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Get timeline of when agents became critical"""
        logs = list(
            self.db['timestep_logs'].find({
                'simulation_id': ObjectId(simulation_id)
            }).sort('timestep', 1)
        )

        return [
            {
                'timestep': log['timestep'],
                'critical_count': log.get('agents_critical', 0),
            }
            for log in logs
        ]

    def get_high_trust_agents(
        self,
        simulation_id: str,
        threshold: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """Get agents with trust score above threshold"""
        agents = list(
            self.db['agents'].find({
                'simulation_id': ObjectId(simulation_id),
                'trust_score': {'$gte': threshold},
            })
        )

        return [
            {
                'id': str(a['_id']),
                'name': a.get('name', ''),
                'type': a.get('agent_type', ''),
                'trust_score': float(a.get('trust_score', 0)),
                'cooperation_level': float(a.get('cooperation_level', 0)),
            }
            for a in agents
        ]

    def get_simulation_summary(self, simulation_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of simulation performance"""
        sim = self.db['simulations'].find_one({'_id': ObjectId(simulation_id)})

        if not sim:
            return {}

        logs = list(
            self.db['timestep_logs'].find({
                'simulation_id': ObjectId(simulation_id)
            })
        )

        if not logs:
            return {
                'simulation_id': simulation_id,
                'name': sim.get('name', ''),
                'timesteps_executed': 0,
                'status': 'no_data',
            }

        stability_scores = [log.get('stability_score', 0) for log in logs]
        risk_levels = [log.get('risk_level', 0) for log in logs]
        fairness_scores = [log.get('fairness_score', 0) for log in logs]
        efficiency = [log.get('allocation_efficiency', 0) for log in logs]

        return {
            'simulation_id': simulation_id,
            'name': sim.get('name', ''),
            'description': sim.get('description', ''),
            'timesteps_executed': len(logs),
            'status': 'completed' if sim.get('is_completed', False) else 'running',
            'stability': {
                'avg': sum(stability_scores) / len(stability_scores) if stability_scores else 0,
                'min': min(stability_scores) if stability_scores else 0,
                'max': max(stability_scores) if stability_scores else 0,
            },
            'risk': {
                'avg': sum(risk_levels) / len(risk_levels) if risk_levels else 0,
                'min': min(risk_levels) if risk_levels else 0,
                'max': max(risk_levels) if risk_levels else 0,
            },
            'fairness': {
                'avg': sum(fairness_scores) / len(fairness_scores) if fairness_scores else 0,
                'min': min(fairness_scores) if fairness_scores else 0,
                'max': max(fairness_scores) if fairness_scores else 0,
            },
            'efficiency': {
                'avg': sum(efficiency) / len(efficiency) if efficiency else 0,
                'min': min(efficiency) if efficiency else 0,
                'max': max(efficiency) if efficiency else 0,
            },
        }

    def compare_simulations(
        self,
        simulation_ids: List[str],
    ) -> List[Dict[str, Any]]:
        """Compare performance across multiple simulations"""
        summaries = []
        for sim_id in simulation_ids:
            summary = self.get_simulation_summary(sim_id)
            if summary:
                summaries.append(summary)

        return summaries

    def get_resource_timeline(self, simulation_id: str) -> List[Dict[str, Any]]:
        """Get resource availability and allocation over time"""
        logs = list(
            self.db['timestep_logs'].find({
                'simulation_id': ObjectId(simulation_id)
            }).sort('timestep', 1)
        )

        return [
            {
                'timestep': log['timestep'],
                'power_available': float(log.get('power_available', 0)),
                'power_allocated': float(log.get('power_allocated', 0)),
                'water_available': float(log.get('water_available', 0)),
                'water_allocated': float(log.get('water_allocated', 0)),
                'power_satisfaction': float(log.get('power_satisfaction_rate', 0)),
                'water_satisfaction': float(log.get('water_satisfaction_rate', 0)),
            }
            for log in logs
        ]

    def get_agent_performance_metrics(
        self,
        simulation_id: str,
    ) -> List[Dict[str, Any]]:
        """Get aggregated performance metrics for all agents"""
        agents = list(
            self.db['agents'].find({
                'simulation_id': ObjectId(simulation_id)
            })
        )

        metrics = []

        for agent in agents:
            allocation_history = list(
                self.db['allocations'].find({
                    'simulation_id': ObjectId(simulation_id),
                    'agent_id': agent['_id'],
                })
            )

            if allocation_history:
                avg_fulfillment = sum(a.get('was_fulfilled', 0) for a in allocation_history) / len(allocation_history)
            else:
                avg_fulfillment = 0.0

            metrics.append({
                'agent_id': str(agent['_id']),
                'name': agent.get('name', ''),
                'type': agent.get('agent_type', ''),
                'allocations_count': len(allocation_history),
                'avg_fulfillment': avg_fulfillment,
                'current_trust': float(agent.get('trust_score', 0)),
                'current_demand': float(agent.get('current_demand', 0)),
                'allocated_resources': float(agent.get('allocated_resources', 0)),
            })

        return metrics
