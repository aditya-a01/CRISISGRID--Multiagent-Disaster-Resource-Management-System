"""
CrisisGrid Backend Engine - API Contract & Deployment Guide
"""

# API ENDPOINTS REFERENCE

## Simulation Management

### 1. Create Simulation
**Endpoint:** `POST /api/v1/simulations/`

**Request Body:**
```json
{
  "name": "Crisis Response Simulation",
  "description": "Multi-agent negotiation test",
  "total_timesteps": 100
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Crisis Response Simulation",
  "description": "Multi-agent negotiation test",
  "current_timestep": 0,
  "total_timesteps": 100,
  "is_running": false,
  "is_completed": false,
  "power_available": 1000.0,
  "water_available": 500.0,
  "stability_score": 1.0,
  "unmet_demand": 0.0,
  "risk_level": 0.0,
  "created_at": "2026-05-04T17:10:30.580148"
}
```

---

### 2. List Simulations
**Endpoint:** `GET /api/v1/simulations/?skip=0&limit=20`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Crisis Response Simulation",
    "current_timestep": 5,
    "total_timesteps": 100,
    "stability_score": 0.95,
    "unmet_demand": 5.0,
    "risk_level": 0.05
  }
]
```

---

### 3. Get Simulation Details
**Endpoint:** `GET /api/v1/simulations/{id}`

**Response:** Same as Create Simulation

---

### 4. Add Agent to Simulation
**Endpoint:** `POST /api/v1/simulations/{id}/agents?agent_type={type}&name={name}&current_demand={demand}&max_demand={max}&min_demand={min}&priority_level={priority}`

**Parameters:**
- `agent_type`: One of `hospital`, `water`, `power`, `emergency`
- `name`: Agent name (string)
- `current_demand`: Current resource requirement (float)
- `max_demand`: Maximum demand (float)
- `min_demand`: Minimum demand (float)
- `priority_level`: Priority multiplier (float, default 1.0)

**Response:**
```json
{
  "id": 1,
  "name": "Central Hospital",
  "agent_type": "hospital",
  "priority_level": 2.0
}
```

---

### 5. Get Simulation Agents
**Endpoint:** `GET /api/v1/simulations/{id}/agents`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Central Hospital",
    "agent_type": "hospital",
    "current_demand": 80.0,
    "allocated_resources": 75.0,
    "unmet_demand": 5.0,
    "trust_score": 0.92,
    "priority_level": 2.0,
    "risk_tolerance": 0.5,
    "cooperation_level": 0.8,
    "behavior_profile": "cooperative"
  }
]
```

---

### 6. Execute Simulation Timestep
**Endpoint:** `POST /api/v1/simulations/{id}/step`

**Response:**
```json
{
  "state": {
    "simulation_id": 1,
    "current_timestep": 5,
    "power_available": 950.0,
    "water_available": 480.0
  },
  "agents": [
    {
      "id": 1,
      "name": "Central Hospital",
      "agent_type": "hospital",
      "current_demand": 80.0,
      "allocated_resources": 75.0,
      "current_bid": 160.0,
      "unmet_demand": 5.0,
      "trust_score": 0.92,
      "priority_level": 2.0,
      "risk_tolerance": 0.5,
      "cooperation_level": 0.8
    }
  ],
  "allocations": [
    {
      "id": 1,
      "agent_id": 1,
      "agent_name": "Central Hospital",
      "agent_type": "hospital",
      "requested": 80.0,
      "allocated": 75.0,
      "unmet": 5.0,
      "satisfaction": 0.9375,
      "resource_type": "power",
      "utility_score": 160.0,
      "was_fulfilled": 0.9375
    }
  ],
  "bids": [
    {
      "agent_id": 1,
      "agent_name": "Central Hospital",
      "agent_type": "hospital",
      "demand": 80.0,
      "bid": 160.0,
      "utility": 160.0
    }
  ],
  "metrics": {
    "stability_score": 0.95,
    "unmet_demand": 5.0,
    "risk_level": 0.05,
    "allocation_efficiency": 0.95,
    "fairness_score": 0.98
  },
  "explanations": [
    "Hospital priority increased due to demand spike",
    "Power dependency satisfied at 85%"
  ]
}
```

---

### 7. Get Simulation Metrics
**Endpoint:** `GET /api/v1/simulations/{id}/metrics`

**Response:**
```json
{
  "stability_score": 0.95,
  "unmet_demand": 5.0,
  "risk_level": 0.05,
  "current_timestep": 5,
  "total_timesteps": 100,
  "progress": 0.05
}
```

---

### 8. Get Allocations
**Endpoint:** `GET /api/v1/simulations/{id}/allocations?timestep={optional}`

**Response:**
```json
[
  {
    "id": 1,
    "simulation_id": 1,
    "agent_id": 1,
    "timestep": 0,
    "resource_type": "power",
    "allocated_amount": 75.0,
    "requested_amount": 80.0,
    "utility_score": 160.0,
    "was_fulfilled": 0.9375,
    "explanation": "Central Hospital satisfied 93.75%"
  }
]
```

---

### 9. Delete Simulation
**Endpoint:** `DELETE /api/v1/simulations/{id}`

**Response:** 204 No Content

---

## Health & Status

### Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "service": "CrisisGrid Backend Engine"
}
```

### Root Endpoint
**Endpoint:** `GET /`

**Response:**
```json
{
  "message": "CrisisGrid Backend Engine - Multi-agent Crisis Response System",
  "version": "v1",
  "docs": "/docs",
  "endpoints": {
    "simulations": "/api/v1/simulations",
    "api_docs": "/docs",
    "openapi": "/openapi.json"
  }
}
```

---

## Deployment Instructions

### Prerequisites
- Python 3.9+
- pip or conda

### Installation

```bash
# Clone/navigate to project
cd c:\Users\admin\Documents\Transformers2

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### Running the Server

```bash
# Development mode with hot reload
python -m uvicorn main:app --reload

# Production mode
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# With workers
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Accessing the API

- **Interactive Documentation:** http://localhost:8000/docs
- **Alternative Documentation:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

### Database Configuration

Configure in `.env`:
```
# SQLite (default)
DATABASE_URL=sqlite:///./crisis_grid.db

# PostgreSQL example
DATABASE_URL=postgresql://user:password@localhost/crisis_grid
```

---

## Example Workflow

### Step 1: Create Simulation
```bash
curl -X POST "http://localhost:8000/api/v1/simulations/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hurricane Response",
    "description": "Simulating hurricane recovery",
    "total_timesteps": 50
  }'
```

### Step 2: Add Agents
```bash
curl -X POST "http://localhost:8000/api/v1/simulations/1/agents?agent_type=hospital&name=Central%20Hospital&current_demand=80&max_demand=100&min_demand=50&priority_level=2.0"

curl -X POST "http://localhost:8000/api/v1/simulations/1/agents?agent_type=power&name=Power%20Grid&current_demand=200&max_demand=500&min_demand=100&priority_level=1.8"

curl -X POST "http://localhost:8000/api/v1/simulations/1/agents?agent_type=water&name=Water%20Supply&current_demand=150&max_demand=300&min_demand=80&priority_level=1.7"

curl -X POST "http://localhost:8000/api/v1/simulations/1/agents?agent_type=emergency&name=Emergency%20Services&current_demand=60&max_demand=80&min_demand=40&priority_level=1.9"
```

### Step 3: Run Simulation
```bash
# Execute timestep 1-50
for i in {1..50}; do
  curl -X POST "http://localhost:8000/api/v1/simulations/1/step"
  sleep 1
done
```

### Step 4: Check Results
```bash
curl "http://localhost:8000/api/v1/simulations/1/metrics"
curl "http://localhost:8000/api/v1/simulations/1/agents"
curl "http://localhost:8000/api/v1/simulations/1/allocations"
```

---

## Key System Features

### 1. Utility-Based Negotiation
Formula: `Utility = (priority × demand × impact × dependency_factor) × behavior_factor × trust_score`

- **Priority**: Agent importance multiplier (hospital > emergency > utility)
- **Demand**: Current resource requirement
- **Impact**: Criticality factor for this timestep
- **Dependency Factor**: How much agent depends on other resources
- **Behavior Factor**: Modified by cooperation/risk tolerance
- **Trust Score**: Historical performance metric

### 2. Resource Allocation Algorithm
1. **Minimum Requirements**: Critical agents (hospital, power) get minimum allocation
2. **Priority Sorting**: Sort by utility, then allocate greedily
3. **Fairness Enforcement**: Remaining resources distributed proportionally to unmet demand
4. **Constraint Checking**: Never exceed available resources

### 3. Dependency Management
- **Power → Water**: Water systems require power (80% impact)
- **Power → Hospital**: Hospital requires power (100% impact)
- **Water → Hospital**: Hospital requires water (90% impact)
- **Power/Water → Emergency**: Emergency services depend on both (60%/70% impact)

### 4. Trust Scoring
Updated each timestep based on:
- **Fairness Metric** (60% weight): Did agent receive fair share?
- **Cooperation Metric** (40% weight): Past satisfaction levels

### 5. Behavioral Adaptation
Agents adjust urgency and risk tolerance based on:
- Recent satisfaction history (last 3 timesteps)
- Low satisfaction (<30%): Increase urgency and risk
- High satisfaction (>80%): Decrease urgency, increase cooperation

### 6. Cascading Failure Detection
Monitors for:
- Critical infrastructure satisfaction <30% (HIGH RISK)
- Hospital dependency satisfaction <40% (CRITICAL)
- Dependent agent satisfaction trends

---

## Performance Metrics

**Per Timestep:**
- Stability Score (0.0-1.0): Overall system health
- Risk Level (0.0-1.0): Cascading failure probability
- Allocation Efficiency: Demand met / Total demand
- Fairness Score: Variance in agent satisfaction
- Unmet Demand: Total unsatisfied resource requirement

---

## Error Handling

### Common Errors

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 204 | Success (no content) |
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
| 500 | Internal server error |

### Example Error Response
```json
{
  "detail": "Simulation not found"
}
```

---

## Database Schema

### Simulations Table
- `id`: Primary key
- `name`: Simulation name
- `description`: Optional description
- `current_timestep`: Current execution position
- `total_timesteps`: Maximum timesteps
- `power_available`: Current power resources
- `water_available`: Current water resources
- `is_running`: Execution status
- `is_completed`: Completion status
- `stability_score`: Current system stability
- `unmet_demand`: Total unmet demand
- `risk_level`: Cascading failure risk

### Agents Table
- `id`: Primary key
- `simulation_id`: Foreign key to simulations
- `agent_type`: Type (hospital, power, water, emergency)
- `name`: Agent name
- `current_demand`: Current resource need
- `allocated_resources`: Resources received
- `trust_score`: Trust metric (0.0-1.0)
- `priority_level`: Demand multiplier
- `behavior_profile`: Behavior type
- `memory_log`: JSON array of past interactions

### Allocations Table
- `id`: Primary key
- `simulation_id`: Foreign key
- `agent_id`: Foreign key to agents
- `timestep`: When allocated
- `resource_type`: power or water
- `allocated_amount`: Amount given
- `requested_amount`: Amount requested
- `utility_score`: Agent's utility score
- `was_fulfilled`: Satisfaction percentage

---

## Scaling & Production Considerations

1. **Database**: Switch from SQLite to PostgreSQL for production
2. **Caching**: Use Redis for simulation state caching
3. **Workers**: Run multiple uvicorn workers behind Nginx
4. **Monitoring**: Add Prometheus metrics and distributed tracing
5. **Logging**: Implement centralized logging (ELK stack)
6. **Rate Limiting**: Add API rate limiting middleware
7. **Authentication**: Implement JWT-based auth for simulations
8. **Async**: Consider async simulation execution for large-scale runs

---

## Support & Documentation

- **API Docs:** http://localhost:8000/docs
- **Simulation Theory:** See README.md
- **Code Documentation:** Inline docstrings in all modules
- **Issues:** Check app/core/ for algorithmic details

