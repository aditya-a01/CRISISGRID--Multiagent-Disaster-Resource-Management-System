# CrisisGrid Database Schema & Management Guide

**Database Manager Role:** Store, retrieve, and maintain consistent data for real-time multi-agent crisis response system.

---

## 📊 Database Overview

### Technology Stack
- **ORM:** SQLAlchemy 2.0.23
- **Backends:** SQLite (development), PostgreSQL (production)
- **Pattern:** Repository pattern with specialized query repositories
- **Transactions:** Atomic updates with rollback support
- **Validation:** CHECK constraints and range validation

### Database Files
```
app/
├── models/
│   ├── base.py                 # Base model with timestamps
│   ├── simulation.py           # Simulation state
│   ├── agent.py               # Agent configuration & state
│   ├── allocation.py          # Resource allocations
│   ├── event.py               # Disaster events
│   └── timestep_log.py        # ✨ NEW: Detailed timestep metrics
├── database/
│   ├── session.py             # Engine & session factory
│   ├── base.py                # Declarative base
│   ├── repository.py          # CRUD repositories + analytics
│   └── db_utils.py            # ✨ NEW: Consistency & optimization
```

---

## 🗄️ Table Schemas

### Table: `simulations`
**Purpose:** Store simulation instance metadata and current state

**Columns:**
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, auto-increment | Unique simulation identifier |
| `name` | VARCHAR(255) | NOT NULL | Simulation name |
| `description` | VARCHAR(1000) | NULLABLE | Free-form description |
| `current_timestep` | INTEGER | NOT NULL, default=0 | Current execution step |
| `total_timesteps` | INTEGER | NOT NULL | Max steps to run |
| `is_running` | BOOLEAN | NOT NULL, default=FALSE | Execution status |
| `is_completed` | BOOLEAN | NOT NULL, default=FALSE | Completion status |
| `power_available` | FLOAT | NOT NULL | Available power capacity |
| `water_available` | FLOAT | NOT NULL | Available water capacity |
| `stability_score` | FLOAT | NOT NULL, CHECK(0-1), default=1.0 | System health (0-1) |
| `unmet_demand` | FLOAT | NOT NULL, CHECK(≥0), default=0.0 | Total unsatisfied requests |
| `risk_level` | FLOAT | NOT NULL, CHECK(0-1), default=0.0 | Cascading failure probability |
| `started_at` | DATETIME | NULLABLE | Execution start time |
| `completed_at` | DATETIME | NULLABLE | Execution completion time |
| `created_at` | DATETIME | NOT NULL | Record creation time |
| `updated_at` | DATETIME | NOT NULL | Last update time |

**Indexes:**
- `idx_simulation_created_at` - Fast sorting by creation time
- `idx_simulation_is_completed` - Fast filtering of completed simulations

**Example:**
```json
{
  "id": 1,
  "name": "Hurricane Recovery",
  "current_timestep": 45,
  "total_timesteps": 120,
  "is_running": true,
  "stability_score": 0.92,
  "risk_level": 0.05,
  "unmet_demand": 12.5
}
```

---

### Table: `agents`
**Purpose:** Store autonomous agent configurations and current state

**Columns:**
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Unique agent identifier |
| `simulation_id` | INTEGER | FK→simulations.id | Parent simulation |
| `agent_type` | ENUM | NOT NULL | hospital \| water \| power \| emergency |
| `name` | VARCHAR(255) | NOT NULL | Agent name |
| `current_demand` | FLOAT | NOT NULL | Current resource need |
| `allocated_resources` | FLOAT | NOT NULL, default=0 | Currently allocated amount |
| `max_demand` | FLOAT | NOT NULL | Maximum possible demand |
| `min_demand` | FLOAT | NOT NULL | Minimum critical need |
| `priority_level` | FLOAT | NOT NULL, CHECK(≥0.5), default=1.0 | Allocation priority |
| `dependency_factor` | FLOAT | NOT NULL, default=1.0 | Cascading failure impact |
| `behavior_profile` | ENUM | NOT NULL | cooperative \| competitive \| adaptive |
| `risk_tolerance` | FLOAT | NOT NULL, CHECK(0-1), default=0.5 | Risk-seeking (0=averse, 1=seeking) |
| `cooperation_level` | FLOAT | NOT NULL, CHECK(0-1), default=0.5 | Cooperation tendency |
| `urgency_bias` | FLOAT | NOT NULL, CHECK(0-1), default=0.5 | Urgency tendency |
| `trust_score` | FLOAT | NOT NULL, CHECK(0-1), default=0.5 | Historical reliability (0-1) |
| `memory_log` | JSON | NOT NULL, default=[] | Past interactions history |
| `current_bid` | FLOAT | NOT NULL, default=0.0 | Latest bid amount |
| `unmet_demand` | FLOAT | NOT NULL, default=0.0 | Unsatisfied request |
| `created_at` | DATETIME | NOT NULL | Creation time |
| `updated_at` | DATETIME | NOT NULL | Last update time |

**Indexes:**
- `idx_agent_simulation_id` - Fast lookup by simulation
- `idx_agent_trust_score` - Find high/low trust agents
- `idx_agent_sim_type` - Composite: find agents by type in simulation

**Memory Log Example:**
```json
[
  {
    "timestep": 0,
    "event": "allocated 75.0/80.0",
    "reward": 0.375,
    "behavior": "cooperative"
  },
  {
    "timestep": 1,
    "event": "allocated 80.0/80.0",
    "reward": 1.0,
    "behavior": "cooperative"
  }
]
```

---

### Table: `allocations`
**Purpose:** Record each resource allocation decision for audit trail and analysis

**Columns:**
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Record identifier |
| `simulation_id` | INTEGER | FK→simulations.id | Parent simulation |
| `agent_id` | INTEGER | FK→agents.id | Recipient agent |
| `timestep` | INTEGER | NOT NULL | Execution step |
| `resource_type` | VARCHAR(50) | NOT NULL | 'power' \| 'water' |
| `allocated_amount` | FLOAT | NOT NULL, CHECK(≥0) | Amount allocated |
| `requested_amount` | FLOAT | NOT NULL, CHECK(≥0) | Amount requested |
| `utility_score` | FLOAT | NOT NULL | Bid utility value |
| `was_fulfilled` | FLOAT | NOT NULL, CHECK(0-1) | Fulfillment % (allocated/requested) |
| `explanation` | VARCHAR(1000) | NULLABLE | Why this allocation |
| `created_at` | DATETIME | NOT NULL | Record time |
| `updated_at` | DATETIME | NOT NULL | Update time |

**Indexes:**
- `idx_allocation_sim_timestep` - Find all allocations at specific time
- `idx_allocation_agent_resource` - Allocation history per agent/resource
- `idx_allocation_resource_type` - Group allocations by resource

**Example:**
```json
{
  "id": 1,
  "simulation_id": 1,
  "agent_id": 2,
  "timestep": 5,
  "resource_type": "power",
  "requested_amount": 200.0,
  "allocated_amount": 180.0,
  "was_fulfilled": 0.90,
  "utility_score": 156.3
}
```

---

### Table: `events`
**Purpose:** Audit trail of disaster events and system perturbations

**Columns:**
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Event identifier |
| `simulation_id` | INTEGER | FK→simulations.id | Parent simulation |
| `timestep` | INTEGER | NOT NULL | When occurred |
| `event_type` | ENUM | NOT NULL | power_outage \| water_shortage \| demand_spike \| infrastructure_failure \| recovery |
| `severity` | FLOAT | NOT NULL, CHECK(0-1) | Impact intensity |
| `affected_agent_type` | VARCHAR(50) | NULLABLE | Affected agent type |
| `description` | VARCHAR(500) | NULLABLE | Event details |
| `created_at` | DATETIME | NOT NULL | Record time |
| `updated_at` | DATETIME | NOT NULL | Update time |

**Indexes:**
- `idx_event_sim_timestep` - Find events at specific time
- `idx_event_type` - Find all events of type

**Example:**
```json
{
  "id": 1,
  "simulation_id": 1,
  "timestep": 10,
  "event_type": "power_outage",
  "severity": 0.45,
  "affected_agent_type": "hospital",
  "description": "Regional grid failure affecting power distribution"
}
```

---

### Table: `timestep_logs` ✨ NEW
**Purpose:** Detailed metrics snapshot per timestep for efficient historical analysis

**Columns:**
| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY | Log record ID |
| `simulation_id` | INTEGER | FK→simulations.id | Parent simulation |
| `timestep` | INTEGER | NOT NULL | Execution step |
| `power_available` | FLOAT | NOT NULL | Available power |
| `water_available` | FLOAT | NOT NULL | Available water |
| `power_allocated` | FLOAT | NOT NULL | Total power allocated |
| `water_allocated` | FLOAT | NOT NULL | Total water allocated |
| `stability_score` | FLOAT | NOT NULL, CHECK(0-1) | System health |
| `risk_level` | FLOAT | NOT NULL, CHECK(0-1) | Failure probability |
| `unmet_demand` | FLOAT | NOT NULL, CHECK(≥0) | Total unsatisfied |
| `allocation_efficiency` | FLOAT | NOT NULL, CHECK(0-1) | % demand met |
| `fairness_score` | FLOAT | NOT NULL, CHECK(0-1) | Satisfaction fairness |
| `total_agents` | INTEGER | NOT NULL | Agent count |
| `agents_satisfied` | INTEGER | NOT NULL | Fully satisfied count |
| `agents_critical` | INTEGER | NOT NULL | Critically undersupplied |
| `events_occurred` | INTEGER | NOT NULL | Event count this step |
| `events_summary` | JSON | NOT NULL | [{type, severity}] |
| `total_bids` | INTEGER | NOT NULL | Bid count |
| `avg_utility_score` | FLOAT | NOT NULL | Average bid utility |
| `highest_utility_score` | FLOAT | NOT NULL | Max bid utility |
| `avg_trust_score` | FLOAT | NOT NULL, default=0.5 | Mean agent trust |
| `min_trust_score` | FLOAT | NOT NULL, default=0.5 | Min agent trust |
| `max_trust_score` | FLOAT | NOT NULL, default=0.5 | Max agent trust |
| `power_satisfaction_rate` | FLOAT | NOT NULL, CHECK(0-1) | Power demand met % |
| `water_satisfaction_rate` | FLOAT | NOT NULL, CHECK(0-1) | Water demand met % |
| `notes` | VARCHAR(1000) | NULLABLE | Summary notes |
| `created_at` | DATETIME | NOT NULL | Record time |
| `updated_at` | DATETIME | NOT NULL | Update time |

**Indexes:**
- `idx_timestep_log_sim_step` - Fast lookup by simulation and timestep
- `idx_timestep_log_created_at` - Sort by creation time

**Why This Table Exists:**
- **Performance:** Avoid summing allocations for metrics; query pre-calculated values
- **Historical Analysis:** Complete snapshot of each timestep state
- **Efficiency:** Store aggregate metrics once, query many times
- **Storage:** ~2KB per timestep vs 100+ KB if recalculating from allocations

---

## 🔐 Data Consistency & Constraints

### CHECK Constraints (Database Level)
```sql
-- Simulations
CHECK (stability_score >= 0.0 AND stability_score <= 1.0)
CHECK (risk_level >= 0.0 AND risk_level <= 1.0)
CHECK (unmet_demand >= 0.0)

-- Agents
CHECK (trust_score >= 0.0 AND trust_score <= 1.0)
CHECK (priority_level >= 0.5)
CHECK (risk_tolerance >= 0.0 AND risk_tolerance <= 1.0)
CHECK (cooperation_level >= 0.0 AND cooperation_level <= 1.0)
CHECK (urgency_bias >= 0.0 AND urgency_bias <= 1.0)

-- Allocations
CHECK (was_fulfilled >= 0.0 AND was_fulfilled <= 1.0)
CHECK (allocated_amount >= 0.0)
CHECK (requested_amount >= 0.0)

-- Events
CHECK (severity >= 0.0 AND severity <= 1.0)

-- Timestep Logs
CHECK (timestep >= 0)
CHECK (stability_score >= 0.0 AND stability_score <= 1.0)
CHECK (risk_level >= 0.0 AND risk_level <= 1.0)
```

### Foreign Key Relationships
```
agents → simulations (cascade delete)
allocations → simulations (cascade delete)
allocations → agents (cascade delete)
events → simulations (cascade delete)
timestep_logs → simulations (cascade delete)
```

---

## 📚 Repository Classes

### SimulationRepository
```python
create(name, description, total_timesteps) → Simulation
get_by_id(id) → Simulation
get_all(skip, limit) → List[Simulation]
update_state(id, current_timestep, metrics...) → Simulation
delete(id) → bool
```

### AgentRepository
```python
create(simulation_id, agent_type, name, ...) → Agent
get_by_id(id) → Agent
get_by_simulation(simulation_id) → List[Agent]
update_state(id, demand, allocated, unmet, trust, bid) → Agent
update_memory(id, memory_log) → Agent
```

### AllocationRepository
```python
create(sim_id, agent_id, timestep, resource, amounts...) → Allocation
get_by_simulation(simulation_id) → List[Allocation]
get_by_timestep(simulation_id, timestep) → List[Allocation]
```

### EventRepository
```python
create(sim_id, timestep, type, severity, ...) → Event
get_by_simulation(simulation_id) → List[Event]
get_by_timestep(simulation_id, timestep) → List[Event]
```

### TimestepLogRepository ✨ NEW
```python
create(sim_id, timestep, metrics...) → TimestepLog
get_by_simulation(simulation_id) → List[TimestepLog]
get_by_timestep(simulation_id, timestep) → TimestepLog
get_range(simulation_id, start, end) → List[TimestepLog]
```

---

## 📊 Analytics Repository

### AnalyticsRepository ✨ NEW

**Historical Analysis:**
```python
get_agent_allocation_history(sim_id, agent_id) → List[Dict]
  # Returns: [{timestep, resource, requested, allocated, fulfilled, utility}, ...]

get_agent_satisfaction_trend(sim_id, agent_id) → List[Tuple[int, float]]
  # Returns: [(timestep, satisfaction_rate), ...]

get_fairness_metrics(sim_id) → Dict
  # Returns: {avg_fairness, min_fairness, max_fairness}

get_stability_trend(sim_id) → List[Dict]
  # Returns: [{timestep, stability, risk, unmet_demand}, ...]

get_critical_agents_timeline(sim_id) → List[Dict]
  # Returns: [{timestep, critical_count}, ...]
```

**Resource Efficiency:**
```python
get_resource_efficiency_by_type(sim_id) → Dict[str, Dict]
  # Returns: {
  #   "power": {total_allocated, total_requested, efficiency},
  #   "water": {...}
  # }
```

**Event Impact:**
```python
get_event_impact_analysis(sim_id) → Dict[str, Dict]
  # Returns: {
  #   "power_outage": {count, avg_severity, avg_risk_after},
  #   "water_shortage": {...}
  # }
```

**Agent Trust:**
```python
get_high_trust_agents(sim_id, threshold=0.8) → List[Dict]
  # Returns: [{id, name, type, trust_score, cooperation_level}, ...]
```

**Summary:**
```python
get_simulation_summary(sim_id) → Dict
  # Returns comprehensive performance snapshot
```

---

## 🔒 Data Consistency Utilities

### DatabaseTransactionManager
```python
execute_atomic_timestep_update(sim_id, timestep, update_fn) → bool
  # Ensures all timestep updates succeed or all fail

execute_safe_deletion(simulation_id) → bool
  # Delete in correct order respecting foreign keys
```

### DataConsistencyValidator
```python
validate_simulation_state(sim_id) → Dict
  # Check: agents belong to sim, allocations valid, metrics in range, sequential timesteps

detect_data_anomalies(sim_id) → Dict
  # Find: missing timesteps, extreme drops, over-allocations

check_cascade_relationships(sim_id) → Dict
  # Verify all foreign key relationships are intact
```

### DatabaseOptimizer
```python
analyze_query_performance() → Dict
  # Returns table row counts

get_index_information() → Dict
  # Lists all indexes and their purposes

estimate_storage_usage() → Dict
  # Estimates database size by table

suggest_optimizations() → List[str]
  # Recommendations for performance and maintenance
```

---

## 🚀 Usage Examples

### Store Timestep Metrics
```python
from app.database.repository import TimestepLogRepository
from app.database.session import SessionLocal

db = SessionLocal()
repo = TimestepLogRepository(db)

log = repo.create(
    simulation_id=1,
    timestep=5,
    power_available=950.0,
    water_available=480.0,
    power_allocated=920.0,
    water_allocated=470.0,
    stability_score=0.95,
    risk_level=0.05,
    unmet_demand=10.0,
    allocation_efficiency=0.98,
    fairness_score=0.92,
    total_agents=4,
    agents_satisfied=3,
    agents_critical=0,
    events_occurred=1,
    events_summary=[{"type": "power_outage", "severity": 0.3}],
    avg_trust_score=0.87,
    power_satisfaction_rate=0.95,
    water_satisfaction_rate=0.98,
    notes="One agent experienced minor shortage"
)
```

### Perform Historical Analysis
```python
from app.database.repository import AnalyticsRepository

db = SessionLocal()
analytics = AnalyticsRepository(db)

# Get agent satisfaction over time
satisfaction = analytics.get_agent_satisfaction_trend(sim_id=1, agent_id=2)
print(satisfaction)  # [(0, 0.95), (1, 0.98), (2, 0.92), ...]

# Get fairness metrics
fairness = analytics.get_fairness_metrics(sim_id=1)
print(fairness)  # {avg_fairness: 0.92, min: 0.85, max: 0.99}

# Get complete summary
summary = analytics.get_simulation_summary(sim_id=1)
print(summary)  # Comprehensive performance snapshot
```

### Validate Data Consistency
```python
from app.database.db_utils import DataConsistencyValidator

db = SessionLocal()
validator = DataConsistencyValidator(db)

# Check for data issues
issues = validator.validate_simulation_state(sim_id=1)
if issues['valid']:
    print("✓ Data is consistent")
else:
    print(f"✗ Found issues: {issues['issues']}")

# Detect anomalies
anomalies = validator.detect_data_anomalies(sim_id=1)
if anomalies['has_anomalies']:
    print(f"⚠ Anomalies detected: {anomalies['anomalies']}")
```

### Atomic Timestep Update
```python
from app.database.db_utils import DatabaseTransactionManager

db = SessionLocal()
txn_manager = DatabaseTransactionManager(db)

def update_timestep(session):
    # Update simulation state
    sim = SimulationRepository(session).update_state(...)
    
    # Update agent states
    for agent in agents:
        AgentRepository(session).update_state(...)
    
    # Record allocations
    for alloc in allocations:
        AllocationRepository(session).create(...)
    
    # Log timestep metrics
    TimestepLogRepository(session).create(...)
    
    return True  # Success

success = txn_manager.execute_atomic_timestep_update(
    simulation_id=1,
    timestep=5,
    update_fn=update_timestep
)

if success:
    print("✓ Timestep 5 committed atomically")
else:
    print("✗ Timestep 5 rolled back due to error")
```

---

## 📈 Performance Optimization

### Query Optimization Tips

**1. Use TimestepLog for Aggregates**
```python
# ✓ GOOD: Single query from cached metrics
metrics = db.query(TimestepLog).filter(
    TimestepLog.timestep == 5
).first()
stability = metrics.stability_score

# ✗ SLOW: Sum allocations every query
allocations = db.query(Allocation).filter(
    Allocation.timestep == 5
).all()
efficiency = sum(a.was_fulfilled) / len(allocations)
```

**2. Use Composite Indexes**
```python
# ✓ GOOD: Uses composite index
allocs = db.query(Allocation).filter(
    Allocation.simulation_id == 1,
    Allocation.timestep == 5
).all()

# ✗ SLOW: Can't use composite index
allocs = db.query(Allocation).filter(
    Allocation.timestep == 5
).all()
```

**3. Pagination for Large Datasets**
```python
# ✓ GOOD: Paginated
sims = SimulationRepository(db).get_all(skip=0, limit=50)

# ✗ SLOW: Load all simulations
sims = db.query(Simulation).all()
```

**4. Select Only Needed Columns**
```python
# ✓ GOOD: Only load needed data
trust_scores = db.query(
    Agent.id, Agent.trust_score
).filter(Agent.simulation_id == 1).all()

# ✗ SLOW: Load entire agent records
agents = db.query(Agent).filter(
    Agent.simulation_id == 1
).all()
```

### Index Strategy

**Composite Indexes Used:**
```
simulations:
  - idx_simulation_created_at        → SELECT ORDER BY created_at
  - idx_simulation_is_completed      → WHERE is_completed = true

agents:
  - idx_agent_simulation_id          → WHERE simulation_id = X
  - idx_agent_trust_score            → WHERE trust_score > 0.8
  - idx_agent_sim_type               → WHERE sim_id = X AND type = Y

allocations:
  - idx_allocation_sim_timestep      → WHERE sim_id = X AND step = Y
  - idx_allocation_agent_resource    → WHERE agent_id = X AND resource = Y
  - idx_allocation_resource_type     → WHERE resource = power/water

events:
  - idx_event_sim_timestep           → WHERE sim_id = X AND step = Y
  - idx_event_type                   → WHERE event_type = X

timestep_logs:
  - idx_timestep_log_sim_step        → WHERE sim_id = X AND step = Y
  - idx_timestep_log_created_at      → SELECT ORDER BY created_at
```

---

## 🗑️ Cleanup & Maintenance

### Safe Simulation Deletion
```python
from app.database.db_utils import DatabaseTransactionManager

db = SessionLocal()
txn_manager = DatabaseTransactionManager(db)

# Delete respects foreign key order
success = txn_manager.execute_safe_deletion(simulation_id=1)

# Deletion order:
# 1. allocations
# 2. events
# 3. timestep_logs
# 4. agents
# 5. simulation
```

### Archive Old Simulations
```python
# Move completed simulations older than 90 days to archive table
# (Implementation: create archive table and transfer records)
```

---

## 📋 Database Schema Diagram

```
simulations (1)
├── agents (N) ─── allocations (N)
├── events (N)
└── timestep_logs (N)

simulations
  ├─ id (PK)
  ├─ name
  ├─ current_timestep
  ├─ power_available
  ├─ stability_score
  └─ created_at

agents
  ├─ id (PK)
  ├─ simulation_id (FK) ──→ simulations.id
  ├─ name
  ├─ trust_score
  ├─ behavior_profile
  └─ memory_log (JSON)

allocations
  ├─ id (PK)
  ├─ simulation_id (FK) ──→ simulations.id
  ├─ agent_id (FK) ──→ agents.id
  ├─ timestep
  ├─ resource_type
  ├─ allocated_amount
  └─ was_fulfilled

events
  ├─ id (PK)
  ├─ simulation_id (FK) ──→ simulations.id
  ├─ timestep
  ├─ event_type
  └─ severity

timestep_logs
  ├─ id (PK)
  ├─ simulation_id (FK) ──→ simulations.id
  ├─ timestep
  ├─ stability_score
  ├─ risk_level
  └─ events_summary (JSON)
```

---

## ✅ Responsibilities Met

✅ **State Storage:** simulations table + timestep_logs table  
✅ **Agent Data:** agents table with memory_log JSON + allocation history  
✅ **Simulation Logs:** timestep_logs captures each step's metrics  
✅ **Data Consistency:** CHECK constraints, foreign keys, atomic transactions  
✅ **Query Support:** TimestepLogRepository + AnalyticsRepository for historical analysis  
✅ **Performance:** Indexed columns, composite indexes, optimized queries  

---

## 📞 Database Manager Contacts

For:
- **Schema Questions** → See app/models/
- **Persistence Operations** → See app/database/repository.py
- **Analytics Queries** → See AnalyticsRepository
- **Data Validation** → See DataConsistencyValidator
- **Optimization** → See DatabaseOptimizer

