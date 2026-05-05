"""MongoDB collection schemas and initialization for CrisisGrid Database Manager"""

# =============================================================================
# MONGODB SCHEMA DEFINITIONS
# =============================================================================

# Collection: simulations
# Purpose: Store crisis response simulation instances and current state
SIMULATIONS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "total_timesteps", "created_at"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "name": {
                "bsonType": "string",
                "description": "Simulation name",
                "minLength": 1,
                "maxLength": 255
            },
            "description": {
                "bsonType": "string",
                "description": "Simulation description",
                "maxLength": 1000
            },
            # Simulation state
            "current_timestep": {
                "bsonType": "int",
                "description": "Current execution step",
                "minimum": 0
            },
            "total_timesteps": {
                "bsonType": "int",
                "description": "Total steps to execute",
                "minimum": 1
            },
            "is_running": {
                "bsonType": "bool",
                "description": "Whether simulation is currently running"
            },
            "is_completed": {
                "bsonType": "bool",
                "description": "Whether simulation has completed"
            },
            # Resource state
            "power_available": {
                "bsonType": "double",
                "description": "Available power capacity",
                "minimum": 0
            },
            "water_available": {
                "bsonType": "double",
                "description": "Available water capacity",
                "minimum": 0
            },
            # Metrics
            "stability_score": {
                "bsonType": "double",
                "description": "System health (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            "unmet_demand": {
                "bsonType": "double",
                "description": "Total unsatisfied requests",
                "minimum": 0
            },
            "risk_level": {
                "bsonType": "double",
                "description": "Cascading failure probability (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            # Timestamps
            "started_at": {"bsonType": "date"},
            "completed_at": {"bsonType": "date"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"}
        }
    }
}

# Collection: agents
# Purpose: Store autonomous agent configurations and current state
AGENTS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["simulation_id", "agent_type", "name", "created_at"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "simulation_id": {
                "bsonType": "objectId",
                "description": "Parent simulation ID"
            },
            "agent_type": {
                "enum": ["hospital", "water", "power", "emergency"],
                "description": "Type of agent"
            },
            "name": {
                "bsonType": "string",
                "description": "Agent name",
                "minLength": 1,
                "maxLength": 255
            },
            # Demand and allocation
            "current_demand": {
                "bsonType": "double",
                "description": "Current resource need",
                "minimum": 0
            },
            "allocated_resources": {
                "bsonType": "double",
                "description": "Currently allocated amount",
                "minimum": 0
            },
            "max_demand": {
                "bsonType": "double",
                "description": "Maximum possible demand",
                "minimum": 0
            },
            "min_demand": {
                "bsonType": "double",
                "description": "Minimum critical need",
                "minimum": 0
            },
            # Priority and dependency
            "priority_level": {
                "bsonType": "double",
                "description": "Allocation priority",
                "minimum": 0.5
            },
            "dependency_factor": {
                "bsonType": "double",
                "description": "Cascading failure impact",
                "minimum": 0,
                "maximum": 1
            },
            # Behavioral characteristics
            "behavior_profile": {
                "enum": ["cooperative", "competitive", "adaptive"],
                "description": "Agent behavior type"
            },
            "risk_tolerance": {
                "bsonType": "double",
                "description": "Risk tolerance (0=averse, 1=seeking)",
                "minimum": 0,
                "maximum": 1
            },
            "cooperation_level": {
                "bsonType": "double",
                "description": "Cooperation tendency",
                "minimum": 0,
                "maximum": 1
            },
            "urgency_bias": {
                "bsonType": "double",
                "description": "Urgency tendency",
                "minimum": 0,
                "maximum": 1
            },
            # Trust and memory
            "trust_score": {
                "bsonType": "double",
                "description": "Historical reliability (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            "memory_log": {
                "bsonType": "array",
                "description": "Past interactions history",
                "items": {
                    "bsonType": "object",
                    "properties": {
                        "timestep": {"bsonType": "int"},
                        "event": {"bsonType": "string"},
                        "reward": {"bsonType": "double"},
                        "behavior": {"bsonType": "string"}
                    }
                }
            },
            # State
            "current_bid": {
                "bsonType": "double",
                "description": "Latest bid amount",
                "minimum": 0
            },
            "unmet_demand": {
                "bsonType": "double",
                "description": "Unsatisfied request",
                "minimum": 0
            },
            # Timestamps
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"}
        }
    }
}

# Collection: allocations
# Purpose: Record each resource allocation decision for audit trail and analysis
ALLOCATIONS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["simulation_id", "agent_id", "timestep", "created_at"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "simulation_id": {
                "bsonType": "objectId",
                "description": "Parent simulation ID"
            },
            "agent_id": {
                "bsonType": "objectId",
                "description": "Recipient agent ID"
            },
            "timestep": {
                "bsonType": "int",
                "description": "Execution step",
                "minimum": 0
            },
            # Allocation details
            "resource_type": {
                "enum": ["power", "water"],
                "description": "Resource type"
            },
            "allocated_amount": {
                "bsonType": "double",
                "description": "Amount allocated",
                "minimum": 0
            },
            "requested_amount": {
                "bsonType": "double",
                "description": "Amount requested",
                "minimum": 0
            },
            "utility_score": {
                "bsonType": "double",
                "description": "Bid utility value"
            },
            # Metadata
            "was_fulfilled": {
                "bsonType": "double",
                "description": "Fulfillment percentage (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            "explanation": {
                "bsonType": "string",
                "description": "Why this allocation was made",
                "maxLength": 1000
            },
            # Timestamps
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"}
        }
    }
}

# Collection: events
# Purpose: Audit trail of disaster events and system perturbations
EVENTS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["simulation_id", "timestep", "event_type", "severity", "created_at"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "simulation_id": {
                "bsonType": "objectId",
                "description": "Parent simulation ID"
            },
            "timestep": {
                "bsonType": "int",
                "description": "When event occurred",
                "minimum": 0
            },
            "event_type": {
                "enum": ["power_outage", "water_shortage", "demand_spike", "infrastructure_failure", "recovery"],
                "description": "Type of disaster event"
            },
            "severity": {
                "bsonType": "double",
                "description": "Impact intensity (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            "affected_agent_type": {
                "enum": ["hospital", "water", "power", "emergency", None],
                "description": "Affected agent type"
            },
            "description": {
                "bsonType": "string",
                "description": "Event details",
                "maxLength": 500
            },
            # Timestamps
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"}
        }
    }
}

# Collection: timestep_logs
# Purpose: Detailed metrics snapshot per timestep for efficient historical analysis
TIMESTEP_LOGS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["simulation_id", "timestep", "created_at"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "simulation_id": {
                "bsonType": "objectId",
                "description": "Parent simulation ID"
            },
            "timestep": {
                "bsonType": "int",
                "description": "Execution step",
                "minimum": 0
            },
            # Resource state
            "power_available": {
                "bsonType": "double",
                "description": "Available power",
                "minimum": 0
            },
            "water_available": {
                "bsonType": "double",
                "description": "Available water",
                "minimum": 0
            },
            "power_allocated": {
                "bsonType": "double",
                "description": "Total power allocated",
                "minimum": 0
            },
            "water_allocated": {
                "bsonType": "double",
                "description": "Total water allocated",
                "minimum": 0
            },
            # Metrics
            "stability_score": {
                "bsonType": "double",
                "description": "System health (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            "risk_level": {
                "bsonType": "double",
                "description": "Failure probability (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            "unmet_demand": {
                "bsonType": "double",
                "description": "Total unsatisfied",
                "minimum": 0
            },
            "allocation_efficiency": {
                "bsonType": "double",
                "description": "Percentage of demand met",
                "minimum": 0,
                "maximum": 1
            },
            "fairness_score": {
                "bsonType": "double",
                "description": "Satisfaction fairness (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            # Count metrics
            "total_agents": {"bsonType": "int"},
            "agents_satisfied": {"bsonType": "int"},
            "agents_critical": {"bsonType": "int"},
            # Event summary
            "events_occurred": {"bsonType": "int"},
            "events_summary": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "properties": {
                        "type": {"bsonType": "string"},
                        "severity": {"bsonType": "double"}
                    }
                }
            },
            # Bid summary
            "total_bids": {"bsonType": "int"},
            "avg_utility_score": {"bsonType": "double"},
            "highest_utility_score": {"bsonType": "double"},
            # Trust metrics
            "avg_trust_score": {"bsonType": "double"},
            "min_trust_score": {"bsonType": "double"},
            "max_trust_score": {"bsonType": "double"},
            # Satisfaction rates
            "power_satisfaction_rate": {
                "bsonType": "double",
                "minimum": 0,
                "maximum": 1
            },
            "water_satisfaction_rate": {
                "bsonType": "double",
                "minimum": 0,
                "maximum": 1
            },
            # Notes
            "notes": {
                "bsonType": "string",
                "maxLength": 1000
            },
            # Timestamps
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"}
        }
    }
}

# Collection: system_state
# Purpose: Store current system state (used for real-time queries)
SYSTEM_STATE_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["simulation_id", "created_at"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "simulation_id": {
                "bsonType": "objectId",
                "description": "Associated simulation ID"
            },
            # Current resources
            "total_power": {
                "bsonType": "double",
                "description": "Total power available",
                "minimum": 0
            },
            "total_water": {
                "bsonType": "double",
                "description": "Total water available",
                "minimum": 0
            },
            "power_allocated": {
                "bsonType": "double",
                "description": "Power allocated in current timestep",
                "minimum": 0
            },
            "water_allocated": {
                "bsonType": "double",
                "description": "Water allocated in current timestep",
                "minimum": 0
            },
            # Agent states summary
            "active_agents": {
                "bsonType": "int",
                "description": "Number of active agents"
            },
            "critical_agents": {
                "bsonType": "int",
                "description": "Number of critically undersupplied agents"
            },
            # System metrics
            "stability": {
                "bsonType": "double",
                "minimum": 0,
                "maximum": 1
            },
            "risk": {
                "bsonType": "double",
                "minimum": 0,
                "maximum": 1
            },
            "unmet_demand": {
                "bsonType": "double",
                "minimum": 0
            },
            # Active events
            "active_events": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "properties": {
                        "event_id": {"bsonType": "objectId"},
                        "type": {"bsonType": "string"},
                        "severity": {"bsonType": "double"}
                    }
                }
            },
            # Timestamps
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"}
        }
    }
}

# =============================================================================
# MONGODB INITIALIZATION SCRIPT
# =============================================================================

"""
MongoDB Initialization Commands - Run in MongoDB Compass or VS Code MongoDB extension

1. Create Database:
   use crisisgrid;

2. Create Collections with Schemas:

   db.createCollection("simulations", {
       validator: <SIMULATIONS_SCHEMA>
   });

   db.createCollection("agents", {
       validator: <AGENTS_SCHEMA>
   });

   db.createCollection("allocations", {
       validator: <ALLOCATIONS_SCHEMA>
   });

   db.createCollection("events", {
       validator: <EVENTS_SCHEMA>
   });

   db.createCollection("timestep_logs", {
       validator: <TIMESTEP_LOGS_SCHEMA>
   });

   db.createCollection("system_state", {
       validator: <SYSTEM_STATE_SCHEMA>
   });

3. Create Indexes for Performance:

   # Simulations
   db.simulations.createIndex({ created_at: -1 });
   db.simulations.createIndex({ is_completed: 1 });
   
   # Agents
   db.agents.createIndex({ simulation_id: 1 });
   db.agents.createIndex({ trust_score: -1 });
   db.agents.createIndex({ simulation_id: 1, agent_type: 1 });
   
   # Allocations
   db.allocations.createIndex({ simulation_id: 1, timestep: 1 });
   db.allocations.createIndex({ agent_id: 1, resource_type: 1 });
   db.allocations.createIndex({ resource_type: 1 });
   
   # Events
   db.events.createIndex({ simulation_id: 1, timestep: 1 });
   db.events.createIndex({ event_type: 1 });
   
   # Timestep Logs
   db.timestep_logs.createIndex({ simulation_id: 1, timestep: 1 });
   db.timestep_logs.createIndex({ created_at: -1 });
   
   # System State
   db.system_state.createIndex({ simulation_id: 1 });
   db.system_state.createIndex({ updated_at: -1 });

4. Verify Collections:
   db.getCollectionNames();
   
5. Check Indexes:
   db.simulations.getIndexes();
   db.agents.getIndexes();
   ... etc
"""
