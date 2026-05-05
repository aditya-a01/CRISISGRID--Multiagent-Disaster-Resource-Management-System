# CrisisGrid Backend Engine - Complete Implementation

## Project Overview

**CrisisGrid Backend Engine** is a production-ready multi-agent crisis response system implementing autonomous negotiation, resource allocation, and behavioral AI.

### Key Capabilities

✅ **Autonomous Agents** - Hospital, Water, Power, Emergency systems with behavioral profiles
✅ **Real-Time Negotiation** - Utility-based bidding for resource allocation
✅ **Behavioral AI** - Risk tolerance, cooperation levels, trust scoring
✅ **Dependency Management** - Prevents cascading failures with dependency graph
✅ **REST API** - Full CRUD operations via FastAPI
✅ **Database Persistence** - SQLite/PostgreSQL support with SQLAlchemy ORM
✅ **Comprehensive Metrics** - Stability, risk, fairness, efficiency scoring

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Server
```bash
python start_server.py
# Or manually:
python -m uvicorn main:app --reload
```

### 3. Access API
- **Interactive Docs:** http://localhost:8000/docs
- **Create Simulation:** `POST /api/v1/simulations/`
- **Add Agents:** `POST /api/v1/simulations/{id}/agents`
- **Run Timestep:** `POST /api/v1/simulations/{id}/step`

---

## Architecture

### Core Components

#### 1. Agent Model (`app/core/agent.py`)
```python
class Agent:
  - agent_type: HOSPITAL | WATER | POWER | EMERGENCY
  - behavior_profile: COOPERATIVE | COMPETITIVE | ADAPTIVE
  - priority_level: float (1.0 to 2.0+)
  - trust_score: float (0.0 to 1.0)
  - memory_log: List[MemoryEntry]
  
  Methods:
  - calculate_utility(impact_score, available_resources) → float
  - submit_bid() → float
  - receive_allocation(amount, timestep) → None
  - update_trust_score(fairness, cooperation) → None
  - adjust_behavior(timestep) → None
```

#### 2. Simulation Engine (`app/core/simulation.py`)
```python
class SimulationEngine:
  - execute_timestep() → Dict
    1. Trigger random disaster events
    2. Agents adjust behavior based on history
    3. Collect bids (utility calculation)
    4. Allocate resources (fairness + constraints)
    5. Update trust scores
    6. Calculate metrics
  
  Metrics:
  - stability_score: System health (0.0-1.0)
  - risk_level: Cascading failure probability
  - allocation_efficiency: Demand met %
  - fairness_score: Satisfaction variance
  - unmet_demand: Total unsatisfied
```

#### 3. Dependency Graph (`app/core/dependency_graph.py`)
```
Power → Water (80% impact)
Power → Hospital (100% impact)
Water → Hospital (90% impact)
Power/Water → Emergency (60%/70% impact)

Prevents cascading failures by:
- Detecting critical infrastructure failure
- Boosting priority of dependent agents
- Monitoring satisfaction cascades
```

#### 4. REST API (`app/routers/simulations.py`)
```
POST   /api/v1/simulations/              Create simulation
GET    /api/v1/simulations/              List simulations
GET    /api/v1/simulations/{id}          Get simulation
POST   /api/v1/simulations/{id}/agents   Add agent
GET    /api/v1/simulations/{id}/agents   Get agents
POST   /api/v1/simulations/{id}/step     Execute timestep
GET    /api/v1/simulations/{id}/metrics  Get metrics
GET    /api/v1/simulations/{id}/allocations  Get allocations
DELETE /api/v1/simulations/{id}          Delete simulation
```

---

## System Algorithms

### Utility Calculation Formula
```
Utility = (priority × demand × impact × dependency_factor) 
        × behavior_factor × trust_score

Where:
- priority ∈ [1.0, 2.0+]  - Agent importance
- demand ∈ [min, max]     - Current need
- impact ∈ [0.0, 1.0]     - Criticality this timestep
- dependency_factor ∈ [0.0, 1.0]  - Dependency level
- behavior_factor         - Modified by behavior profile
- trust_score ∈ [0.0, 1.0]  - Historical performance

Behavior Factor:
  - COOPERATIVE: 0.8 + cooperation_level × 0.2
  - COMPETITIVE: 1.2 + risk_tolerance × 0.3
  - ADAPTIVE: Adjusts based on scarcity_ratio
```

### Resource Allocation Algorithm

**Step 1: Critical Minimums**
- Hospital: 50 units minimum
- Power: 30 units minimum
- Water: 30 units minimum

**Step 2: Priority Sorting**
- Sort agents by: adjusted_priority × utility_score
- Higher priority agents allocate first

**Step 3: Greedy Allocation**
- Allocate up to requested amount
- Respect total capacity constraints
- Track unmet demand

**Step 4: Fairness Enforcement**
- Calculate fair share: demand / total_demand
- Distribute remaining resources proportionally
- Minimize satisfaction variance

**Step 5: Constraint Checking**
- Never exceed power_capacity
- Never exceed water_capacity
- Never violate minimum requirements for hospital

---

## Agent Behavioral Profiles

### 1. COOPERATIVE Agents
- **Strategy:** Moderate demands, respect fairness
- **Behavior Factor:** 0.8 to 1.0
- **Use Case:** Water systems, reliable infrastructure
- **Adaptation:** Increase cooperation when satisfied

### 2. COMPETITIVE Agents
- **Strategy:** Maximize own allocation
- **Behavior Factor:** 1.2 to 1.5
- **Use Case:** Emergency services during crisis
- **Adaptation:** Increase urgency when unsatisfied

### 3. ADAPTIVE Agents
- **Strategy:** Adjust based on resource scarcity
- **Behavior Factor:** 0.9 to 1.1 (dynamic)
- **Use Case:** Hospital, flexible systems
- **Adaptation:** Respond to conditions in real-time

---

## Trust Scoring System

### Update Formula
```
new_trust = 0.7 × old_trust + 0.3 × (fairness × 0.6 + cooperation × 0.4)

Where:
- fairness ∈ [0.0, 1.0] - Did agent get fair share?
- cooperation ∈ [0.0, 1.0] - Past satisfaction average
```

### Impact on Decisions
- **Trust Score 0.9+:** Agent has priority
- **Trust Score 0.5-0.9:** Normal allocation
- **Trust Score <0.5:** Lower priority, higher scrutiny

---

## Cascading Failure Detection

### Risk Factors
1. **Critical Infrastructure Failure**
   - Power satisfaction <30% → Risk += 0.3
   - Water satisfaction <30% → Risk += 0.15

2. **Dependent Agent Risk**
   - Hospital dependency satisfaction <40% → Risk += 0.4
   - Emergency services constraint → Risk += 0.2

3. **System Instability**
   - Rapid satisfaction changes → Monitor for cascades
   - Multiple agent failures → Exponential risk increase

### Prevention Mechanisms
- Boost priority when dependencies fail
- Enforce hospital minimum requirements
- Monitor satisfaction trends (3-timestep window)
- Alert system when risk >0.7

---

## Data Models

### Simulation
```json
{
  "id": 1,
  "name": "Hurricane Response",
  "current_timestep": 5,
  "total_timesteps": 100,
  "is_running": true,
  "is_completed": false,
  "power_available": 950.0,
  "water_available": 480.0,
  "stability_score": 0.95,
  "unmet_demand": 5.0,
  "risk_level": 0.05,
  "created_at": "2026-05-04T17:10:30"
}
```

### Agent
```json
{
  "id": 1,
  "name": "Central Hospital",
  "agent_type": "hospital",
  "current_demand": 80.0,
  "allocated_resources": 75.0,
  "unmet_demand": 5.0,
  "trust_score": 0.92,
  "priority_level": 2.0,
  "behavior_profile": "cooperative",
  "risk_tolerance": 0.5,
  "cooperation_level": 0.8,
  "urgency_bias": 0.4,
  "dependency_factor": 1.0,
  "memory_log": [
    {"timestep": 0, "event": "allocated 75.0/80.0", "reward": 0.375},
    ...
  ]
}
```

### Allocation
```json
{
  "id": 1,
  "agent_id": 1,
  "agent_name": "Central Hospital",
  "timestep": 0,
  "resource_type": "power",
  "requested": 80.0,
  "allocated": 75.0,
  "unmet": 5.0,
  "satisfaction": 0.9375,
  "utility_score": 160.0,
  "was_fulfilled": 0.9375
}
```

---

## Example Usage

### Create a Crisis Response Simulation
```bash
curl -X POST "http://localhost:8000/api/v1/simulations/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hurricane Recovery",
    "description": "5-day post-hurricane recovery",
    "total_timesteps": 120
  }'

# Response: {"id": 1, ...}
```

### Add Agents
```bash
# Hospital
curl -X POST "http://localhost:8000/api/v1/simulations/1/agents" \
  -d "agent_type=hospital&name=Central%20Hospital&current_demand=80&max_demand=100&min_demand=50&priority_level=2.0"

# Power
curl -X POST "http://localhost:8000/api/v1/simulations/1/agents" \
  -d "agent_type=power&name=Power%20Grid&current_demand=200&max_demand=500&min_demand=100&priority_level=1.8"

# Water
curl -X POST "http://localhost:8000/api/v1/simulations/1/agents" \
  -d "agent_type=water&name=Water%20Supply&current_demand=150&max_demand=300&min_demand=80&priority_level=1.7"

# Emergency
curl -X POST "http://localhost:8000/api/v1/simulations/1/agents" \
  -d "agent_type=emergency&name=Emergency%20Services&current_demand=60&max_demand=80&min_demand=40&priority_level=1.9"
```

### Run Simulation
```bash
# Execute 5 timesteps
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/v1/simulations/1/step" | jq
done
```

### Monitor Metrics
```bash
curl "http://localhost:8000/api/v1/simulations/1/metrics" | jq

# Response:
# {
#   "stability_score": 0.95,
#   "risk_level": 0.05,
#   "unmet_demand": 5.0,
#   "progress": 0.042
# }
```

---

## Testing

### Unit Tests
```bash
python -m pytest tests/test_core.py -v
```

### Integration Tests
```bash
python -m pytest tests/test_api.py -v
```

### Manual Testing
```python
from app.core.agent import Agent, AgentType
from app.core.simulation import SimulationEngine

# Create agents
hospital = Agent(1, AgentType.HOSPITAL, "Central Hospital", 80, 100, 50, 2.0)
power = Agent(2, AgentType.POWER, "Power Grid", 200, 500, 100, 1.8)

# Create engine
engine = SimulationEngine(1, "Test", 100)
engine.add_agent(hospital)
engine.add_agent(power)

# Run
for step in range(5):
    result = engine.execute_timestep()
    print(f"Step {step}: Stability={result['metrics']['stability_score']:.2f}")
```

---

## Deployment

### Development
```bash
python start_server.py
```

### Production
```bash
# With multiple workers
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Optional)
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

---

## Performance Characteristics

- **Single Timestep:** ~10-50ms (4 agents)
- **Database Operations:** ~5ms per operation
- **Memory per Agent:** ~2KB
- **Concurrent Users:** Limited by uvicorn workers (recommend 4-8)

---

## Future Enhancements

1. **Async Execution:** Parallel agent negotiation
2. **Advanced AI:** Deep learning for agent behavior
3. **Real-time Dashboard:** WebSocket updates
4. **Multi-region Support:** Distributed simulations
5. **Event Streaming:** Kafka integration
6. **Advanced Analytics:** Predictive failure modeling

---

## License & Support

See LICENSE file for terms.

For issues, check API_CONTRACT.md for detailed endpoint documentation.

## Directory Structure

```
CrisisGrid/
├── app/
│   ├── core/                 # Core simulation engine
│   │   ├── agent.py         # Agent model with behavioral AI
│   │   ├── simulation.py     # SimulationEngine with negotiation
│   │   └── dependency_graph.py  # Dependency & failure detection
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic validation schemas
│   ├── database/            # Database session & repository
│   └── routers/             # FastAPI endpoint routers
├── tests/                   # Unit & integration tests
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── API_CONTRACT.md          # Complete API specification
├── README.md                # This file
└── start_server.py          # Startup script with checks
```

---

## Version History

- **v1.0.0** (May 2026) - Initial release with core features
  - Multi-agent negotiation
  - Resource allocation
  - Dependency management
  - REST API with database persistence

