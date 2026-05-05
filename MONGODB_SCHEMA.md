# CrisisGrid MongoDB Database Schema

**Document Version:** 1.0  
**Last Updated:** 2024  
**Status:** Production Ready  
**Purpose:** Comprehensive guide to MongoDB data persistence layer for CrisisGrid crisis response system

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Collections Reference](#collections-reference)
3. [Data Relationships](#data-relationships)
4. [Indexing Strategy](#indexing-strategy)
5. [Query Examples](#query-examples)
6. [Best Practices](#best-practices)
7. [Performance Optimization](#performance-optimization)
8. [Integration Guide](#integration-guide)

---

## Architecture Overview

### Database Concept

MongoDB provides a document-oriented data store for CrisisGrid with:

- **BSON Schema Validation**: Enforces data consistency at database level
- **Aggregation Pipelines**: Efficient analytical queries without application-level processing
- **Flexible Indexing**: Multi-field and composite indexes for performance
- **Transactions**: ACID support for multi-document atomic operations
- **Horizontal Scalability**: Foundation for sharding and replication

### Why MongoDB vs SQLite?

| Aspect | SQLite | MongoDB |
|--------|--------|---------|
| Complex Analytics | Python processing needed | Aggregation pipelines |
| Schema Flexibility | Fixed schema | Flexible embedding |
| Scalability | Single file | Horizontal scaling |
| Real-time Queries | Row-based | Document embedding |
| Concurrent Writes | Limited | Highly optimized |

### Module Structure

```
app/mongo_db/
├── __init__.py                 # Module exports
├── schemas.py                  # BSON schema definitions
├── connection.py               # Client lifecycle & initialization
├── repository.py               # CRUD operations (7 repositories)
├── analytics.py                # Complex analytical queries
└── db_utils.py                 # Transactions, validation, optimization
```

---

## Collections Reference

### 1. Simulations Collection

**Purpose:** Tracks simulation runs, metadata, and overall system state

**Document Structure:**

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "Crisis Scenario 2024-Q1",
  "description": "Earthquake response with cascading failures",
  "current_timestep": 42,
  "total_timesteps": 500,
  "is_running": true,
  "is_completed": false,
  "power_available": 1000.0,
  "water_available": 500.0,
  "stability_score": 0.72,
  "unmet_demand": 15.3,
  "risk_level": 0.48,
  "started_at": ISODate("2024-01-15T10:00:00Z"),
  "completed_at": null,
  "created_at": ISODate("2024-01-15T10:00:00Z"),
  "updated_at": ISODate("2024-01-15T10:15:42Z")
}
```

**Field Descriptions:**

| Field | Type | Range | Purpose |
|-------|------|-------|---------|
| `_id` | ObjectId | — | Unique simulation ID |
| `name` | String | 1-255 chars | Human-readable title |
| `description` | String | 0-1000 chars | Scenario details |
| `current_timestep` | Int | 0-N | Progress indicator |
| `total_timesteps` | Int | 1-10000 | Planned duration |
| `is_running` | Boolean | true/false | Execution status |
| `is_completed` | Boolean | true/false | Completion flag |
| `power_available` | Double | ≥0 | Total power (units) |
| `water_available` | Double | ≥0 | Total water (units) |
| `stability_score` | Double | 0.0-1.0 | System health metric |
| `unmet_demand` | Double | ≥0 | Unfulfilled requests |
| `risk_level` | Double | 0.0-1.0 | System risk metric |
| `started_at` | Date | — | Execution start time |
| `completed_at` | Date | — | Execution end time (null if running) |
| `created_at` | Date | — | Record creation timestamp |
| `updated_at` | Date | — | Last modification timestamp |

**Indexes:**

```javascript
db.simulations.createIndex({ created_at: -1 }, { name: 'idx_created_at' });
db.simulations.createIndex({ is_completed: 1 }, { name: 'idx_is_completed' });
```

**CRUD Operations via Repository:**

```python
from app.mongo_db.repository import SimulationRepository

# Create
sim = repo.create(
    name="Scenario A",
    description="Test run",
    total_timesteps=100
)

# Read
sim = repo.get_by_id(simulation_id)
sims = repo.get_all(skip=0, limit=10)

# Update
success = repo.update_state(
    simulation_id,
    current_timestep=50,
    stability_score=0.75
)

# Delete
success = repo.delete(simulation_id)
```

---

### 2. Agents Collection

**Purpose:** Stores agent state, behavioral profiles, and trust history

**Document Structure:**

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439012"),
  "simulation_id": ObjectId("507f1f77bcf86cd799439011"),
  "agent_type": "hospital",
  "name": "Central Hospital District 1",
  "current_demand": 85.5,
  "allocated_resources": 72.0,
  "max_demand": 150.0,
  "min_demand": 10.0,
  "priority_level": 1.0,
  "dependency_factor": 0.8,
  "behavior_profile": "cooperative",
  "risk_tolerance": 0.3,
  "cooperation_level": 0.9,
  "urgency_bias": 0.6,
  "trust_score": 0.87,
  "memory_log": [
    {
      "timestep": 0,
      "event": "allocation_denied",
      "severity": 0.5
    },
    {
      "timestep": 1,
      "event": "allocation_granted",
      "severity": 0.0
    }
  ],
  "current_bid": 85.5,
  "unmet_demand": 13.5,
  "created_at": ISODate("2024-01-15T10:00:00Z"),
  "updated_at": ISODate("2024-01-15T10:15:42Z")
}
```

**Field Descriptions:**

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `_id` | ObjectId | — | Unique agent ID |
| `simulation_id` | ObjectId | — | Reference to parent simulation |
| `agent_type` | String | hospital, water, power, emergency | Agent category |
| `name` | String | 1-255 chars | Display name |
| `current_demand` | Double | ≥0 | Current resource request |
| `allocated_resources` | Double | ≥0 | Allocation received |
| `max_demand` | Double | ≥0 | Upper demand limit |
| `min_demand` | Double | ≥0 | Lower demand limit |
| `priority_level` | Double | 0.5-10.0 | Urgency weight |
| `dependency_factor` | Double | 0.0-1.0 | Multi-resource dependency |
| `behavior_profile` | String | cooperative, competitive, adaptive | Decision model |
| `risk_tolerance` | Double | 0.0-1.0 | Acceptable loss level |
| `cooperation_level` | Double | 0.0-1.0 | Collaboration tendency |
| `urgency_bias` | Double | 0.0-1.0 | Demand inflation factor |
| `trust_score` | Double | 0.0-1.0 | Reputation metric |
| `memory_log` | Array | — | Historical events (embedded) |
| `current_bid` | Double | ≥0 | Latest auction bid |
| `unmet_demand` | Double | ≥0 | Shortfall from request |

**Indexes:**

```javascript
db.agents.createIndex({ simulation_id: 1 }, { name: 'idx_simulation_id' });
db.agents.createIndex({ trust_score: -1 }, { name: 'idx_trust_score' });
db.agents.createIndex({ simulation_id: 1, agent_type: 1 }, { name: 'idx_sim_type' });
```

**Memory Log Array Schema:**

```json
{
  "timestep": 5,
  "event": "allocation_denied",
  "severity": 0.7,
  "details": "Insufficient water available"
}
```

---

### 3. Allocations Collection

**Purpose:** Records all resource allocation decisions (audit trail)

**Document Structure:**

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439013"),
  "simulation_id": ObjectId("507f1f77bcf86cd799439011"),
  "agent_id": ObjectId("507f1f77bcf86cd799439012"),
  "timestep": 42,
  "resource_type": "power",
  "allocated_amount": 72.0,
  "requested_amount": 85.5,
  "utility_score": 0.84,
  "was_fulfilled": 0.84,
  "explanation": "Allocated 84% of request due to resource constraints",
  "created_at": ISODate("2024-01-15T10:15:42Z"),
  "updated_at": ISODate("2024-01-15T10:15:42Z")
}
```

**Field Descriptions:**

| Field | Type | Range | Purpose |
|-------|------|-------|---------|
| `_id` | ObjectId | — | Unique allocation ID |
| `simulation_id` | ObjectId | — | Simulation reference (FK) |
| `agent_id` | ObjectId | — | Agent reference (FK) |
| `timestep` | Int | ≥0 | Simulation timestep |
| `resource_type` | String | power, water | Resource category |
| `allocated_amount` | Double | ≥0 | Granted quantity |
| `requested_amount` | Double | ≥0 | Requested quantity |
| `utility_score` | Double | -∞ to +∞ | Satisfaction metric |
| `was_fulfilled` | Double | 0.0-1.0 | Fulfillment ratio |
| `explanation` | String | 0-1000 chars | Decision rationale |

**Indexes:**

```javascript
db.allocations.createIndex(
  { simulation_id: 1, timestep: 1 },
  { name: 'idx_sim_timestep' }
);
db.allocations.createIndex(
  { agent_id: 1, resource_type: 1 },
  { name: 'idx_agent_resource' }
);
db.allocations.createIndex({ resource_type: 1 }, { name: 'idx_resource_type' });
```

---

### 4. Events Collection

**Purpose:** Records disasters, infrastructure failures, and recovery events

**Document Structure:**

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439014"),
  "simulation_id": ObjectId("507f1f77bcf86cd799439011"),
  "timestep": 35,
  "event_type": "power_outage",
  "severity": 0.9,
  "affected_agent_type": "hospital",
  "description": "Grid substation 7 offline due to earthquake damage",
  "created_at": ISODate("2024-01-15T10:14:00Z"),
  "updated_at": ISODate("2024-01-15T10:14:00Z")
}
```

**Field Descriptions:**

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `_id` | ObjectId | — | Unique event ID |
| `simulation_id` | ObjectId | — | Simulation reference (FK) |
| `timestep` | Int | ≥0 | When event occurred |
| `event_type` | String | See enum below | Crisis type |
| `severity` | Double | 0.0-1.0 | Impact intensity |
| `affected_agent_type` | String | hospital, water, power, emergency, null | Primary impact target |
| `description` | String | 0-500 chars | Event details |

**Event Types:**

- `power_outage`: Grid or local power loss
- `water_shortage`: Supply reduction or contamination
- `demand_spike`: Sudden increase in requests
- `infrastructure_failure`: Equipment breakdown
- `recovery`: System restoration milestone

**Indexes:**

```javascript
db.events.createIndex(
  { simulation_id: 1, timestep: 1 },
  { name: 'idx_sim_timestep' }
);
db.events.createIndex({ event_type: 1 }, { name: 'idx_event_type' });
```

---

### 5. Timestep Logs Collection

**Purpose:** Pre-aggregated metrics for each simulation timestep

**Document Structure:**

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439015"),
  "simulation_id": ObjectId("507f1f77bcf86cd799439011"),
  "timestep": 42,
  "power_available": 1000.0,
  "water_available": 500.0,
  "power_allocated": 958.0,
  "water_allocated": 485.0,
  "stability_score": 0.72,
  "risk_level": 0.48,
  "unmet_demand": 15.3,
  "allocation_efficiency": 0.89,
  "fairness_score": 0.76,
  "total_agents": 12,
  "agents_satisfied": 10,
  "agents_critical": 1,
  "events_occurred": 0,
  "events_summary": [],
  "total_bids": 12,
  "avg_utility_score": 0.82,
  "highest_utility_score": 0.98,
  "avg_trust_score": 0.75,
  "min_trust_score": 0.42,
  "max_trust_score": 0.95,
  "power_satisfaction_rate": 0.91,
  "water_satisfaction_rate": 0.87,
  "notes": "Stable conditions, minor demand spike at end of step",
  "created_at": ISODate("2024-01-15T10:15:42Z"),
  "updated_at": ISODate("2024-01-15T10:15:42Z")
}
```

**Field Descriptions (23 Metrics):**

| Field | Type | Range | Purpose |
|-------|------|-------|---------|
| `timestep` | Int | ≥0 | Step identifier |
| `power_available` | Double | ≥0 | Total power (units) |
| `water_available` | Double | ≥0 | Total water (units) |
| `power_allocated` | Double | ≥0 | Power distributed |
| `water_allocated` | Double | ≥0 | Water distributed |
| `stability_score` | Double | 0.0-1.0 | System health |
| `risk_level` | Double | 0.0-1.0 | Crisis indicator |
| `unmet_demand` | Double | ≥0 | Unfulfilled requests |
| `allocation_efficiency` | Double | 0.0-1.0 | Resource utilization |
| `fairness_score` | Double | 0.0-1.0 | Distribution equity |
| `total_agents` | Int | ≥0 | Agent count |
| `agents_satisfied` | Int | ≥0 | Fulfilled agents |
| `agents_critical` | Int | ≥0 | Emergency agents |
| `events_occurred` | Int | ≥0 | Event count |
| `events_summary` | Array | — | Event details |
| `total_bids` | Int | ≥0 | Allocation requests |
| `avg_utility_score` | Double | -∞ to +∞ | Mean satisfaction |
| `highest_utility_score` | Double | -∞ to +∞ | Peak satisfaction |
| `avg_trust_score` | Double | 0.0-1.0 | Mean reputation |
| `min_trust_score` | Double | 0.0-1.0 | Lowest reputation |
| `max_trust_score` | Double | 0.0-1.0 | Highest reputation |
| `power_satisfaction_rate` | Double | 0.0-1.0 | Power fulfillment % |
| `water_satisfaction_rate` | Double | 0.0-1.0 | Water fulfillment % |

**Indexes:**

```javascript
db.timestep_logs.createIndex(
  { simulation_id: 1, timestep: 1 },
  { name: 'idx_sim_timestep' }
);
db.timestep_logs.createIndex({ created_at: -1 }, { name: 'idx_created_at' });
```

---

### 6. System State Collection

**Purpose:** Real-time snapshot of current simulation state (one document per simulation)

**Document Structure:**

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439016"),
  "simulation_id": ObjectId("507f1f77bcf86cd799439011"),
  "total_power": 1000.0,
  "total_water": 500.0,
  "power_allocated": 958.0,
  "water_allocated": 485.0,
  "active_agents": 12,
  "critical_agents": 1,
  "stability": 0.72,
  "risk": 0.48,
  "unmet_demand": 15.3,
  "active_events": [
    {
      "event_id": "507f1f77bcf86cd799439014",
      "event_type": "power_outage",
      "severity": 0.9,
      "started_at": 35
    }
  ],
  "created_at": ISODate("2024-01-15T10:15:42Z"),
  "updated_at": ISODate("2024-01-15T10:15:42Z")
}
```

**Field Descriptions:**

| Field | Type | Purpose |
|-------|------|---------|
| `_id` | ObjectId | Unique state ID |
| `simulation_id` | ObjectId | Simulation reference (FK) |
| `total_power` | Double | Available power supply |
| `total_water` | Double | Available water supply |
| `power_allocated` | Double | Power granted to agents |
| `water_allocated` | Double | Water granted to agents |
| `active_agents` | Int | Non-idle agent count |
| `critical_agents` | Int | Agents in critical status |
| `stability` | Double | Current system health |
| `risk` | Double | Current crisis level |
| `unmet_demand` | Double | Total unfulfilled requests |
| `active_events` | Array | Currently relevant events |

**Indexes:**

```javascript
db.system_state.createIndex({ simulation_id: 1 }, { name: 'idx_simulation_id' });
db.system_state.createIndex({ updated_at: -1 }, { name: 'idx_updated_at' });
```

---

## Data Relationships

### Foreign Key Pattern

MongoDB uses ObjectId references instead of SQL foreign keys:

```
Simulations (1) ──── (N) Agents
     │
     ├── (1) ──── (N) Allocations
     ├── (1) ──── (N) Events
     ├── (1) ──── (N) Timestep Logs
     └── (1) ──── (1) System State

Agents (1) ──── (N) Allocations
```

### Cascading Deletes

When deleting a simulation, use `execute_safe_deletion()`:

```python
from app.mongo_db.db_utils import MongoDBTransactionManager

success = txn_manager.execute_safe_deletion(simulation_id)
# Deletes in order:
# 1. Allocations
# 2. Events
# 3. Timestep Logs
# 4. System State
# 5. Agents
# 6. Simulation
```

---

## Indexing Strategy

### Index Types

**Single-field Indexes:**
- For filtering: `simulation_id`, `is_completed`, `trust_score`
- For sorting: `created_at`, `updated_at`, `timestep`

**Compound Indexes:**
- Query combinations: `(simulation_id, timestep)`, `(agent_id, resource_type)`
- For efficient scanning of multi-condition queries

### Performance Impact

| Index | Expected Queries/sec | Without Index |
|-------|----------------------|---------------|
| idx_sim_timestep | 10,000+ | 500-1,000 |
| idx_created_at | 5,000+ | 100-200 |
| idx_trust_score | 2,000+ | 50-100 |

### When to Add Indexes

Add an index if:
1. Query appears in application logs 50+ times/hour
2. Query scan involves >1000 documents
3. Sort on field takes >100ms

### Storage Cost

```
Total index size ≈ 15-20% of collection size
Example: 1 million allocations ≈ 50-75 MB in indexes
```

---

## Query Examples

### Common Read Operations

**Get all agents in a simulation:**

```python
from app.mongo_db.repository import AgentRepository

agents = repo.get_by_simulation(simulation_id="507f...")
```

**Get allocation history for an agent:**

```python
from app.mongo_db.analytics import AnalyticsRepository

history = analytics.get_agent_allocation_history(
    simulation_id="507f...",
    agent_id="507f..."
)
```

**Get timestep 42 metrics:**

```python
log = repo.get_by_timestep(
    simulation_id="507f...",
    timestep=42
)
```

### Analytical Queries

**Get fairness metrics:**

```python
fairness = analytics.get_fairness_metrics(simulation_id="507f...")
# Returns: {avg_fairness, min_fairness, max_fairness}
```

**Get stability trend:**

```python
trend = analytics.get_stability_trend(simulation_id="507f...")
# Returns: [{timestep, stability, risk, unmet_demand}, ...]
```

**Compare multiple simulations:**

```python
comparison = analytics.compare_simulations([
    "507f1f77bcf86cd799439011",
    "507f1f77bcf86cd799439017",
])
```

### Aggregation Pipeline Examples

**Resource efficiency by type:**

```python
pipeline = [
    {'$match': {'simulation_id': ObjectId(sim_id)}},
    {
        '$group': {
            '_id': '$resource_type',
            'total_allocated': {'$sum': '$allocated_amount'},
            'total_requested': {'$sum': '$requested_amount'},
            'avg_fulfillment': {'$avg': '$was_fulfilled'},
        }
    }
]
results = db['allocations'].aggregate(pipeline)
```

**High-trust agents:**

```python
db.agents.find(
    {
        'simulation_id': ObjectId(sim_id),
        'trust_score': {'$gte': 0.8}
    }
).sort('trust_score', -1).limit(10)
```

---

## Best Practices

### DO:

✅ **Use ObjectId for document references:**
```python
agent_ref = ObjectId(agent_id)  # Correct
```

✅ **Validate ObjectId before queries:**
```python
if ObjectId.is_valid(id_string):
    result = db.find_one({'_id': ObjectId(id_string)})
```

✅ **Use transactions for multi-document updates:**
```python
txn_manager.execute_atomic_timestep_update(sim_id, timestep, update_fn)
```

✅ **Embed memory_log in agents:**
```python
agent = {
    'name': 'Hospital A',
    'memory_log': [  # Embedded array
        {'timestep': 0, 'event': 'allocation_denied', 'severity': 0.5}
    ]
}
```

✅ **Use aggregation for analytics:**
```python
# Good: Database-side aggregation
results = db['allocations'].aggregate([...])

# Avoid: Loading all docs in Python
all_docs = list(db['allocations'].find({}))
# ... process in Python
```

### DON'T:

❌ **Don't use string IDs:**
```python
# Wrong
result = db.find_one({'agent_id': '507f1f77bcf86cd799439012'})

# Correct
result = db.find_one({'agent_id': ObjectId('507f1f77bcf86cd799439012')})
```

❌ **Don't embed unbounded arrays:**
```python
# Wrong: events array can grow to 16MB limit
agent = {
    'name': 'Hospital',
    'events': [...]  # Could overflow
}

# Correct: Reference external collection
agent = {
    'name': 'Hospital',
}
# Query events separately by agent_id
```

❌ **Don't use find() + Python filtering:**
```python
# Wrong: Loads everything into memory
agents = [a for a in db['agents'].find({}) if a['trust_score'] > 0.8]

# Correct: Filter in database
agents = list(db['agents'].find({'trust_score': {'$gt': 0.8}}))
```

---

## Performance Optimization

### Query Optimization

**Use explain() to analyze queries:**

```python
from app.mongo_db.db_utils import MongoDBOptimizer

optimizer = MongoDBOptimizer(db)
optimizer.analyze_query_performance()
# Returns collection document counts
```

**Projection to reduce data transfer:**

```python
# Get only needed fields
allocations = db['allocations'].find(
    {'simulation_id': sim_id},
    {'resource_type': 1, 'allocated_amount': 1}  # Projection
)
```

### Bulk Operations

**Batch writes for efficiency:**

```python
from pymongo import InsertOne

operations = [
    InsertOne({'simulation_id': sim_id, 'timestep': i, ...})
    for i in range(1000)
]
db['timestep_logs'].bulk_write(operations)
```

### Connection Pooling

**Configured in connection.py:**

```python
client = MongoClient(
    mongodb_url,
    connectTimeoutMS=5000,
    retryWrites=True,
    w='majority',  # Write concern
)
```

---

## Integration Guide

### Setup

1. **Run initialization script:**

```bash
mongosh < mongodb_init.js
```

2. **Configure settings:**

```python
# config.py
mongodb_url = "mongodb://localhost:27017"
mongodb_database = "crisisgrid"
use_mongodb = True
```

3. **Initialize connection:**

```python
from app.mongo_db.connection import MongoDBConnection, MongoDBInitializer

connection = MongoDBConnection()
connection.connect()  # Singleton connect

initializer = MongoDBInitializer(connection.get_database())
initializer.initialize_all()  # Create collections & indexes
initializer.verify_setup()    # Verify everything
```

### Using Repositories in FastAPI

```python
from fastapi import Depends
from app.mongo_db.connection import get_mongodb
from app.mongo_db.repository import SimulationRepository

@app.get("/simulations/{simulation_id}")
def get_simulation(simulation_id: str, db = Depends(get_mongodb)):
    repo = SimulationRepository(db)
    return repo.get_by_id(simulation_id)
```

---

## Monitoring & Maintenance

### Health Check

```python
connection.connect()
# Pings admin database and verifies all collections exist
```

### Backup

```bash
mongodump --uri="mongodb://localhost:27017" --out=./backup
```

### Restore

```bash
mongorestore --uri="mongodb://localhost:27017" ./backup
```

---

## Conclusion

This MongoDB schema provides:

✅ **Data Consistency**: BSON validation + referential integrity  
✅ **Performance**: Optimized indexes + aggregation pipelines  
✅ **Scalability**: Document-oriented design supporting horizontal growth  
✅ **Maintainability**: Clear relationships and comprehensive documentation  
✅ **Real-time Capability**: Fast queries for live simulation dashboards  

**Next Steps:**
1. Review each collection definition with domain experts
2. Test with production-like data volumes
3. Monitor query performance patterns
4. Adjust indexes based on actual usage
5. Plan archiving strategy for completed simulations
