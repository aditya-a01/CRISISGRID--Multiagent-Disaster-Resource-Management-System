# CrisisGrid Database Manager - Quick Reference & Operations Guide

**Role:** Ensure reliable data storage, real-time query performance, and data consistency for multi-agent simulations.

---

## 🎯 Quick Start

### Import Required Classes
```python
from app.database.repository import (
    SimulationRepository,
    AgentRepository,
    AllocationRepository,
    EventRepository,
    TimestepLogRepository,
    AnalyticsRepository,
)
from app.database.db_utils import (
    DatabaseTransactionManager,
    DataConsistencyValidator,
    DatabaseOptimizer,
)
from app.database.session import SessionLocal
```

### Get Database Session
```python
db = SessionLocal()
try:
    # Your database operations here
    repo = SimulationRepository(db)
    sim = repo.get_by_id(1)
finally:
    db.close()
```

---

## 📋 Common Operations

### Creating a New Simulation
```python
repo = SimulationRepository(db)

sim = repo.create(
    name="Hurricane Response",
    description="5-day recovery simulation",
    total_timesteps=120
)
print(f"Created simulation {sim.id}")
```

### Adding Agents to Simulation
```python
agent_repo = AgentRepository(db)

hospital = agent_repo.create(
    simulation_id=1,
    agent_type="hospital",
    name="Central Hospital",
    current_demand=80.0,
    max_demand=100.0,
    min_demand=50.0,
    priority_level=2.0
)
```

### Recording Timestep Metrics
```python
log_repo = TimestepLogRepository(db)

log = log_repo.create(
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
    notes="System recovered from minor outage"
)
```

### Recording Allocations
```python
alloc_repo = AllocationRepository(db)

alloc = alloc_repo.create(
    simulation_id=1,
    agent_id=1,
    timestep=5,
    resource_type="power",
    allocated_amount=75.0,
    requested_amount=80.0,
    utility_score=156.3,
    was_fulfilled=0.9375
)
```

### Recording Events
```python
event_repo = EventRepository(db)

event = event_repo.create(
    simulation_id=1,
    timestep=10,
    event_type="power_outage",
    severity=0.45,
    affected_agent_type="hospital",
    description="Regional grid failure"
)
```

---

## 📊 Analysis Operations

### Get Agent Satisfaction History
```python
analytics = AnalyticsRepository(db)

satisfaction = analytics.get_agent_satisfaction_trend(
    simulation_id=1,
    agent_id=2
)
# Returns: [(timestep, satisfaction_rate), ...]
# Example: [(0, 0.95), (1, 0.98), (2, 0.92)]

# Plot satisfaction over time
import matplotlib.pyplot as plt
timesteps = [t for t, _ in satisfaction]
rates = [r for _, r in satisfaction]
plt.plot(timesteps, rates)
plt.xlabel('Timestep')
plt.ylabel('Satisfaction Rate')
plt.title('Agent Satisfaction Over Time')
plt.show()
```

### Analyze Resource Efficiency
```python
efficiency = analytics.get_resource_efficiency_by_type(simulation_id=1)

for resource, stats in efficiency.items():
    print(f"\n{resource.upper()}:")
    print(f"  Total Allocated: {stats['total_allocated']:.1f}")
    print(f"  Total Requested: {stats['total_requested']:.1f}")
    print(f"  Efficiency: {stats['efficiency']:.1%}")
```

### Evaluate Fairness
```python
fairness = analytics.get_fairness_metrics(simulation_id=1)

print(f"Fairness Analysis:")
print(f"  Average: {fairness['avg_fairness']:.2f}")
print(f"  Range: {fairness['min_fairness']:.2f} - {fairness['max_fairness']:.2f}")

if fairness['avg_fairness'] > 0.9:
    print("  Status: ✓ Excellent fairness")
elif fairness['avg_fairness'] > 0.7:
    print("  Status: ⚠ Good fairness with improvements")
else:
    print("  Status: ✗ Poor fairness - needs attention")
```

### Track Stability Trends
```python
stability_trend = analytics.get_stability_trend(simulation_id=1)

for point in stability_trend:
    print(f"Step {point['timestep']}: "
          f"Stability={point['stability']:.2f}, "
          f"Risk={point['risk']:.2f}, "
          f"Unmet={point['unmet_demand']:.1f}")
```

### Analyze Event Impact
```python
impact = analytics.get_event_impact_analysis(simulation_id=1)

for event_type, metrics in impact.items():
    print(f"\n{event_type}:")
    print(f"  Occurrences: {metrics['count']}")
    print(f"  Avg Severity: {metrics['avg_severity']:.2f}")
    print(f"  Risk After: {metrics['avg_risk_after']:.2f}")
```

### Find High-Trust Agents
```python
high_trust = analytics.get_high_trust_agents(
    simulation_id=1,
    threshold=0.85
)

print(f"Agents with trust > 0.85:")
for agent in high_trust:
    print(f"  {agent['name']} ({agent['type']}): "
          f"trust={agent['trust_score']:.2f}, "
          f"cooperation={agent['cooperation_level']:.2f}")
```

### Get Comprehensive Summary
```python
summary = analytics.get_simulation_summary(simulation_id=1)

print(f"\nSimulation: {summary['name']}")
print(f"Status: {summary['status']}")
print(f"Timesteps Executed: {summary['timesteps_executed']}")

print(f"\nStability:")
print(f"  Average: {summary['stability']['avg']:.2f}")
print(f"  Range: {summary['stability']['min']:.2f} - {summary['stability']['max']:.2f}")

print(f"\nRisk:")
print(f"  Average: {summary['risk']['avg']:.2f}")
print(f"  Range: {summary['risk']['min']:.2f} - {summary['risk']['max']:.2f}")

print(f"\nAllocation Efficiency:")
print(f"  Average: {summary['efficiency']['avg']:.1%}")
print(f"  Range: {summary['efficiency']['min']:.1%} - {summary['efficiency']['max']:.1%}")
```

---

## 🔒 Data Validation & Consistency

### Validate Simulation State
```python
validator = DataConsistencyValidator(db)

state_report = validator.validate_simulation_state(simulation_id=1)

if state_report['valid']:
    print("✓ Simulation state is valid")
    print(f"  Agents: {state_report['agent_count']}")
    print(f"  Allocations: {state_report['allocation_count']}")
else:
    print("✗ Data integrity issues found:")
    for issue in state_report['issues']:
        print(f"  - {issue}")

if state_report['warnings']:
    print("⚠ Warnings:")
    for warning in state_report['warnings']:
        print(f"  - {warning}")
```

### Detect Anomalies
```python
anomalies_report = validator.detect_data_anomalies(simulation_id=1)

print(f"Timestep logs: {anomalies_report['timestep_logs_count']}")

if anomalies_report['has_anomalies']:
    print("⚠ Anomalies detected:")
    for anomaly in anomalies_report['anomalies']:
        print(f"  - {anomaly}")
else:
    print("✓ No anomalies detected")
```

### Check Data Relationships
```python
cascade_report = validator.check_cascade_relationships(simulation_id=1)

if cascade_report['valid']:
    print("✓ All foreign key relationships are intact")
else:
    print("✗ Relationship issues:")
    for issue in cascade_report['issues']:
        print(f"  - {issue}")
```

---

## 🚀 Atomic Operations

### Atomic Timestep Update
```python
txn_manager = DatabaseTransactionManager(db)

def update_timestep_fn(session):
    """This function must succeed completely or fail completely"""
    
    sim_repo = SimulationRepository(session)
    agent_repo = AgentRepository(session)
    alloc_repo = AllocationRepository(session)
    log_repo = TimestepLogRepository(session)
    
    # 1. Update simulation state
    sim = sim_repo.update_state(
        simulation_id=1,
        current_timestep=5,
        power_available=950.0,
        water_available=480.0,
        stability_score=0.95,
        risk_level=0.05,
        unmet_demand=10.0
    )
    
    # 2. Update agent states
    for agent_id, demand, allocated, unmet, trust, bid in agents_data:
        agent_repo.update_state(
            agent_id=agent_id,
            current_demand=demand,
            allocated_resources=allocated,
            unmet_demand=unmet,
            trust_score=trust,
            current_bid=bid
        )
    
    # 3. Record allocations
    for alloc_data in allocations_list:
        alloc_repo.create(**alloc_data)
    
    # 4. Log timestep metrics
    log_repo.create(
        simulation_id=1,
        timestep=5,
        # ... all metrics
    )
    
    return True  # Success

# Execute atomically
success = txn_manager.execute_atomic_timestep_update(
    simulation_id=1,
    timestep=5,
    update_fn=update_timestep_fn
)

if success:
    print("✓ Timestep 5 committed atomically")
else:
    print("✗ Timestep 5 rolled back - all changes reverted")
```

### Safe Deletion
```python
txn_manager = DatabaseTransactionManager(db)

# Deletes: allocations → events → logs → agents → simulation
success = txn_manager.execute_safe_deletion(simulation_id=1)

if success:
    print("✓ Simulation and all data deleted safely")
else:
    print("✗ Deletion failed - transaction rolled back")
```

---

## 📈 Performance Monitoring

### Database Statistics
```python
optimizer = DatabaseOptimizer(db)

stats = optimizer.analyze_query_performance()
print("Database Statistics:")
for table, count in stats.items():
    print(f"  {table}: {count} records")
```

### Index Information
```python
indexes = optimizer.get_index_information()
print("Database Indexes:")
for table, index_list in indexes.items():
    print(f"  {table}:")
    for idx in index_list:
        print(f"    - {idx}")
```

### Storage Estimation
```python
storage = optimizer.estimate_storage_usage()
print("Storage Usage (Estimates):")
for item, size in storage.items():
    if item != 'note':
        print(f"  {item}: {size}")
```

### Optimization Suggestions
```python
suggestions = optimizer.suggest_optimizations()
print("Optimization Recommendations:")
for i, suggestion in enumerate(suggestions, 1):
    print(f"  {i}. {suggestion}")
```

---

## ⚠️ Best Practices

### DO ✓

**1. Use TimestepLog for Aggregates**
```python
# ✓ GOOD: Single efficient query
log = log_repo.get_by_timestep(sim_id=1, timestep=5)
stability = log.stability_score

# Instead of: summing allocations every time
```

**2. Validate Before Updating**
```python
# ✓ GOOD: Check data validity first
is_valid = validator.validate_simulation_state(sim_id)['valid']
if is_valid:
    # Proceed with update
    txn_manager.execute_atomic_timestep_update(...)
```

**3. Use Pagination**
```python
# ✓ GOOD: Load in chunks
page1 = sim_repo.get_all(skip=0, limit=50)
page2 = sim_repo.get_all(skip=50, limit=50)

# Instead of: loading all simulations into memory
```

**4. Batch Operations Atomically**
```python
# ✓ GOOD: All or nothing
txn_manager.execute_atomic_timestep_update(
    simulation_id=1,
    timestep=5,
    update_fn=batch_update_function
)
```

**5. Select Only Needed Columns**
```python
# ✓ GOOD: When doing analytics on just trust scores
high_trust = analytics.get_high_trust_agents(sim_id=1, threshold=0.8)

# Instead of: loading entire agent objects
```

### DON'T ✗

**1. Load All Data Into Memory**
```python
# ✗ BAD: Loads all 1M allocations
all_allocations = db.query(Allocation).all()

# ✓ GOOD: Use analytics queries with pre-calculated metrics
metrics = analytics.get_resource_efficiency_by_type(sim_id)
```

**2. Multiple Queries in Loop**
```python
# ✗ BAD: N+1 problem - 1000 queries
for agent_id in agent_ids:
    agent = agent_repo.get_by_id(agent_id)
    print(agent.trust_score)

# ✓ GOOD: Single query
high_trust_agents = analytics.get_high_trust_agents(sim_id, threshold=0.7)
```

**3. Nested Transactions Without Rollback**
```python
# ✗ BAD: If inner operation fails, data is inconsistent
sim_repo.update_state(...)
agent_repo.update_state(...)  # What if this fails?
alloc_repo.create(...)

# ✓ GOOD: Atomic all-or-nothing
txn_manager.execute_atomic_timestep_update(..., update_fn)
```

**4. Delete Without Validation**
```python
# ✗ BAD: What if simulation has foreign key references?
db.delete(simulation)
db.commit()

# ✓ GOOD: Use safe deletion with correct order
txn_manager.execute_safe_deletion(simulation_id)
```

**5. Skip Data Validation**
```python
# ✗ BAD: Invalid data silently stored
repo.create(name=agent.name, trust_score=1.5)  # Out of range!

# ✓ GOOD: Validate before operations
validator.validate_simulation_state(sim_id)
```

---

## 🔍 Debugging Query Performance

### Enable Query Logging
```python
import logging
from sqlalchemy.pool import StaticPool

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Now all SQL queries will be printed
```

### Identify Slow Queries
```python
# If a query is slow, check:
# 1. Is there an index on the filter column?
# 2. Are you using SELECT *?
# 3. Are you fetching too much data?
# 4. Should you use TimestepLog instead of Allocation?
```

### Check Index Usage
```python
# Get index suggestions
suggestions = optimizer.suggest_optimizations()
# Implementation varies by database backend
```

---

## 📝 Common Queries Reference

### Find All Simulations for User
```python
sims = sim_repo.get_all(skip=0, limit=100)
```

### Get Latest Simulation Status
```python
sim = sim_repo.get_by_id(sim_id)
print(f"Timestep: {sim.current_timestep}/{sim.total_timesteps}")
print(f"Status: {'Running' if sim.is_running else 'Stopped'}")
```

### Agent Demand Evolution
```python
allocations = analytics.get_agent_allocation_history(sim_id, agent_id)
for alloc in allocations:
    print(f"Step {alloc['timestep']}: "
          f"demand={alloc['requested']}, "
          f"got={alloc['allocated']}")
```

### Fairness Over Time
```python
logs = log_repo.get_by_simulation(sim_id)
for log in logs:
    print(f"Step {log.timestep}: fairness={log.fairness_score:.2f}")
```

### Event Timeline
```python
events = event_repo.get_by_simulation(sim_id)
for evt in events:
    print(f"Step {evt.timestep}: {evt.event_type} "
          f"(severity={evt.severity:.2f})")
```

---

## 🚨 Error Handling

### Gracefully Handle Missing Data
```python
sim = sim_repo.get_by_id(999)
if sim is None:
    print("Simulation not found")
    # Handle appropriately
else:
    print(f"Found: {sim.name}")
```

### Transaction Rollback
```python
try:
    txn_manager.execute_atomic_timestep_update(
        simulation_id=1,
        timestep=5,
        update_fn=risky_update
    )
except Exception as e:
    print(f"Update failed: {e}")
    # Transaction automatically rolled back
    # Database is in consistent state
```

---

## ✅ Checklist: Responsibilities Met

- ✅ **State Storage:** Simulations table + current timestep state
- ✅ **Resource Availability:** power_available, water_available tracked per step
- ✅ **Active Events:** Events table records all disaster events
- ✅ **Agent Data:** Demand history, allocation history, behavior, trust, memory
- ✅ **Simulation Logs:** TimestepLog records each step's metrics
- ✅ **Negotiation Results:** Bids and allocations recorded
- ✅ **System Metrics:** Stability, risk, fairness tracked
- ✅ **Data Consistency:** CHECK constraints, foreign keys, atomic transactions
- ✅ **Query Support:** Real-time retrieval + historical analysis
- ✅ **Performance:** Indexes, composite keys, aggregated queries

---

## 📞 Database Manager Support

**For issues with:**
- Slow queries → Check index usage (DatabaseOptimizer)
- Data inconsistency → Run validation (DataConsistencyValidator)
- Atomicity issues → Use DatabaseTransactionManager
- Historical analysis → Use AnalyticsRepository
- New queries → Extend AnalyticsRepository

