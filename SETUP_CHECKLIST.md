# MongoDB + CrisisGrid Setup Checklist

## ✅ Completed
- [x] Python environment configured (venv with 3.12.6)
- [x] PyMongo driver installed
- [x] FastAPI and all dependencies ready
- [x] MongoDB Python modules created (6 files)
- [x] main.py updated for MongoDB support

## 📥 Next Steps (Do These Now)

### Step 1: Install MongoDB Community Edition
**Status:** ⏳ In Progress

1. Download from: https://www.mongodb.com/try/download/community
2. Choose **Windows 64-bit**
3. Run the `.msi` installer
4. Accept default installation (installs as Windows Service)
5. MongoDB will auto-start as a service
6. ✅ **Verify:** Open new terminal and run:
   ```bash
   mongosh --eval "db.adminCommand('ping')"
   ```
   Should return: `{ ok: 1 }`

### Step 2: Initialize MongoDB Database
**Status:** ⏳ Waiting for MongoDB

Once MongoDB is installed and running:

```bash
cd c:\Users\admin\Documents\Transformers2
mongosh < mongodb_init.js
```

This will:
- Create 6 collections (simulations, agents, allocations, events, timestep_logs, system_state)
- Add BSON schema validation
- Create 15+ performance indexes
- Display verification summary

**Expected Output:**
```
✓ Created simulations collection
✓ Created agents collection
✓ Created allocations collection
✓ Created events collection
✓ Created timestep_logs collection
✓ Created system_state collection
✓ Created simulations indexes
✓ Created agents indexes
✓ Created allocations indexes
✓ Created events indexes
✓ Created timestep_logs indexes
✓ Created system_state indexes

=== MongoDB Setup Complete ===
```

### Step 3: Configure App for MongoDB
**Status:** ✅ Ready

Your `config.py` already has:
```python
mongodb_url = "mongodb://localhost:27017"
mongodb_database = "crisisgrid"
use_mongodb = True  # This enables MongoDB!
```

### Step 4: Run the App
**Status:** ✅ Ready

Once MongoDB is initialized, start the app:

```bash
cd c:\Users\admin\Documents\Transformers2
.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✓ Connected to MongoDB
✓ MongoDB initialized with collections and indexes
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Press CTRL+C to quit
```

### Step 5: Test the API
**Status:** ✅ Ready after Step 4

Open browser:
```
http://localhost:8000/docs
```

Use Postman for a quick end-to-end check (MongoDB ObjectIds are 24 hex chars).

1) Create simulation
```http
POST http://localhost:8000/api/v1/simulations/
Content-Type: application/json

{
   "name": "Postman Test Simulation",
   "description": "Created via Postman",
   "total_timesteps": 10
}
```
Copy the `_id` from the response.

2) Get simulation
```http
GET http://localhost:8000/api/v1/simulations/{SIM_ID}
```

3) Add agent to simulation
```http
POST http://localhost:8000/api/v1/simulations/{SIM_ID}/agents?agent_type=hospital&name=Central%20Hospital&current_demand=40&max_demand=100&min_demand=10&priority_level=1.0&behavior_profile=cooperative
```
Copy the agent `_id` from the response.

4) List agents
```http
GET http://localhost:8000/api/v1/simulations/{SIM_ID}/agents
```

5) Create allocation
```http
POST http://localhost:8000/api/v1/allocations/
Content-Type: application/json

{
   "simulation_id": "{SIM_ID}",
   "agent_id": "{AGENT_ID}",
   "timestep": 1,
   "resource_type": "power",
   "allocated_amount": 25.0,
   "requested_amount": 40.0,
   "utility_score": 0.62,
   "was_fulfilled": 0.625
}
```

6) List allocations
```http
GET http://localhost:8000/api/v1/allocations?simulation_id={SIM_ID}
```

7) Create event
```http
POST http://localhost:8000/api/v1/events/
Content-Type: application/json

{
   "simulation_id": "{SIM_ID}",
   "timestep": 1,
   "event_type": "power_outage",
   "severity": 0.4,
   "affected_agent_type": "hospital",
   "description": "Local grid failure"
}
```

8) List events
```http
GET http://localhost:8000/api/v1/events?simulation_id={SIM_ID}
```

9) Create timestep log
```http
POST http://localhost:8000/api/v1/timestep-logs/
Content-Type: application/json

{
   "simulation_id": "{SIM_ID}",
   "timestep": 1,
   "power_available": 950.0,
   "water_available": 480.0,
   "power_allocated": 50.0,
   "water_allocated": 20.0,
   "stability_score": 0.92,
   "risk_level": 0.08,
   "unmet_demand": 5.0,
   "allocation_efficiency": 0.9,
   "fairness_score": 0.88,
   "total_agents": 1,
   "agents_satisfied": 1,
   "agents_critical": 0,
   "events_occurred": 1,
   "events_summary": [
      { "type": "power_outage", "severity": 0.4 }
   ],
   "total_bids": 1,
   "avg_utility_score": 0.62,
   "highest_utility_score": 0.62,
   "avg_trust_score": 0.5,
   "min_trust_score": 0.5,
   "max_trust_score": 0.5,
   "power_satisfaction_rate": 0.625,
   "water_satisfaction_rate": 1.0,
   "notes": "First timestep log"
}
```

10) List timestep logs
```http
GET http://localhost:8000/api/v1/timestep-logs?simulation_id={SIM_ID}
```

11) Analytics examples
```http
GET http://localhost:8000/api/v1/analytics/summary?simulation_id={SIM_ID}
GET http://localhost:8000/api/v1/analytics/stability?simulation_id={SIM_ID}
GET http://localhost:8000/api/v1/analytics/fairness?simulation_id={SIM_ID}
GET http://localhost:8000/api/v1/analytics/event-impact?simulation_id={SIM_ID}
GET http://localhost:8000/api/v1/analytics/resource-efficiency?simulation_id={SIM_ID}
GET http://localhost:8000/api/v1/analytics/agent-allocation-history?simulation_id={SIM_ID}&agent_id={AGENT_ID}
GET http://localhost:8000/api/v1/analytics/agent-satisfaction?simulation_id={SIM_ID}&agent_id={AGENT_ID}
GET http://localhost:8000/api/v1/analytics/critical-agents?simulation_id={SIM_ID}
GET http://localhost:8000/api/v1/analytics/high-trust-agents?simulation_id={SIM_ID}&threshold=0.5
```

## 🎯 Timeline

| Step | Action | Time | Status |
|------|--------|------|--------|
| 1 | Download & Install MongoDB | 5-10 min | ⏳ In Progress |
| 2 | Run initialization script | 1 min | ⏳ Waiting |
| 3 | Configure app | Already done | ✅ |
| 4 | Start FastAPI server | 1 min | ⏳ Waiting |
| 5 | Test endpoints | 5 min | ⏳ Waiting |

**Total Time:** ~20 minutes

## 🔧 Troubleshooting

### MongoDB not found after install?
```bash
# Verify MongoDB is running
mongosh --version

# Check service (Windows)
Get-Service MongoDB
```

### Schema initialization fails?
```bash
# Check if MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Manually check collections
mongosh
> use crisisgrid
> show collections
```

### App won't start?
```bash
# Check Python installation
python --version

# Test MongoDB connection
python -c "from pymongo import MongoClient; MongoClient().admin.command('ping')"
```

## 📖 Documentation

- [MONGODB_SCHEMA.md](MONGODB_SCHEMA.md) - Complete collection reference
- [MONGODB_IMPLEMENTATION.md](MONGODB_IMPLEMENTATION.md) - API guide and examples
- [API_CONTRACT.md](API_CONTRACT.md) - REST endpoint specifications

## ✨ After Setup

Once everything is running:

1. **Create a simulation:**
   ```bash
   curl -X POST http://localhost:8000/simulations/ \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","description":"Test run","total_timesteps":100}'
   ```

2. **View MongoDB data:**
   ```bash
   mongosh
   > use crisisgrid
   > db.simulations.find()
   ```

3. **Browse API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

**Questions?** Check the [MONGODB_IMPLEMENTATION.md](MONGODB_IMPLEMENTATION.md) for detailed examples and troubleshooting.
