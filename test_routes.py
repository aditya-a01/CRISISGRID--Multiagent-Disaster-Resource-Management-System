"""
Comprehensive route testing for CrisisGrid API
Tests all endpoints across multiple simulation scenarios.
"""
import requests
import json
import sys

API = "http://localhost:8000/api/v1"
PASS = 0
FAIL = 0
created_sim_ids = []

def log(status, route, method, detail=""):
    global PASS, FAIL
    icon = "PASS" if status else "FAIL"
    if status:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{icon}] {method:6s} {route:50s} {detail}")

def test_health():
    print("\n=== Health Check ===")
    r = requests.get("http://localhost:8000/health")
    log(r.status_code == 200, "/health", "GET", f"status={r.status_code}")
    r2 = requests.get("http://localhost:8000/")
    log(r2.status_code == 200, "/", "GET", f"status={r2.status_code}")

def test_create_simulation(name, timesteps):
    """POST /simulations/ - Create a new simulation"""
    r = requests.post(f"{API}/simulations/", json={
        "name": name,
        "description": f"Test: {name}",
        "total_timesteps": timesteps,
    })
    ok = r.status_code == 200 and "_id" in r.json()
    data = r.json() if ok else {}
    log(ok, "/simulations/", "POST", f"name={name}, id={data.get('_id','?')}")
    if ok:
        sim_id = data["_id"]
        created_sim_ids.append(sim_id)
        # Validate response fields
        expected_fields = ["_id", "name", "total_timesteps", "current_timestep",
                           "is_running", "is_completed", "power_available", "water_available",
                           "stability_score", "unmet_demand", "risk_level"]
        missing = [f for f in expected_fields if f not in data]
        if missing:
            log(False, "/simulations/ response", "POST", f"missing fields: {missing}")
        else:
            log(True, "/simulations/ response fields", "POST", "all expected fields present")
        return sim_id
    return None

def test_list_simulations():
    """GET /simulations/ - List all simulations"""
    r = requests.get(f"{API}/simulations/")
    ok = r.status_code == 200 and isinstance(r.json(), list)
    log(ok, "/simulations/", "GET", f"count={len(r.json()) if ok else '?'}")
    return r.json() if ok else []

def test_get_simulation(sim_id):
    """GET /simulations/{id} - Get a specific simulation"""
    r = requests.get(f"{API}/simulations/{sim_id}")
    ok = r.status_code == 200 and r.json().get("_id") == sim_id
    log(ok, f"/simulations/{sim_id[:8]}...", "GET", f"name={r.json().get('name','?')}")

def test_get_simulation_404():
    """GET /simulations/{bad_id} - Should return 404"""
    r = requests.get(f"{API}/simulations/000000000000000000000000")
    log(r.status_code == 404, "/simulations/bad_id", "GET", f"status={r.status_code} (expect 404)")

def test_add_agent(sim_id, agent_type, name, demand, max_d, min_d, priority):
    """POST /simulations/{id}/agents - Add an agent"""
    r = requests.post(
        f"{API}/simulations/{sim_id}/agents",
        params={
            "agent_type": agent_type,
            "name": name,
            "current_demand": demand,
            "max_demand": max_d,
            "min_demand": min_d,
            "priority_level": priority,
        }
    )
    ok = r.status_code == 200 and "_id" in r.json()
    log(ok, f"/simulations/{sim_id[:8]}../agents", "POST", f"agent={name}")
    return r.json().get("_id") if ok else None

def test_get_agents(sim_id, expected_count=None):
    """GET /simulations/{id}/agents - List agents"""
    r = requests.get(f"{API}/simulations/{sim_id}/agents")
    ok = r.status_code == 200 and isinstance(r.json(), list)
    count = len(r.json()) if ok else 0
    if expected_count is not None:
        ok = ok and count == expected_count
    log(ok, f"/simulations/{sim_id[:8]}../agents", "GET", f"count={count}")
    return r.json() if ok else []

def test_step(sim_id, step_num):
    """POST /simulations/{id}/step - Execute a step"""
    r = requests.post(f"{API}/simulations/{sim_id}/step")
    ok = r.status_code == 200
    data = r.json() if ok else {}
    ts = data.get("state", {}).get("current_timestep", "?")
    stab = data.get("metrics", {}).get("stability_score", "?")
    risk = data.get("metrics", {}).get("risk_level", "?")
    agents_count = len(data.get("agents", []))
    event = data.get("event")
    expls = data.get("explanations", [])

    log(ok, f"/simulations/{sim_id[:8]}../step", "POST",
        f"step={step_num} ts={ts} stab={stab} risk={risk}")

    # Validate step response structure
    if ok:
        required = ["state", "agents", "allocations", "bids", "metrics"]
        missing = [f for f in required if f not in data]
        if missing:
            log(False, f"  step response fields", "POST", f"missing: {missing}")
        else:
            log(True, f"  step response fields", "POST", f"agents={agents_count} event={'yes' if event else 'no'} expls={len(expls)}")

        # Validate agents have expected fields
        if data.get("agents"):
            a = data["agents"][0]
            agent_fields = ["name", "agent_type", "current_demand",
                            "allocated_resources", "trust_score", "priority_level",
                            "behavior_profile"]
            a_missing = [f for f in agent_fields if f not in a]
            if a_missing:
                log(False, f"  agent fields", "POST", f"missing: {a_missing}")
            else:
                log(True, f"  agent fields", "POST", "all expected fields present")

        # Validate metrics
        m = data.get("metrics", {})
        metric_fields = ["stability_score", "risk_level", "allocation_efficiency",
                         "fairness_score", "unmet_demand"]
        m_missing = [f for f in metric_fields if f not in m]
        if m_missing:
            log(False, f"  metrics fields", "POST", f"missing: {m_missing}")
        else:
            log(True, f"  metrics fields", "POST", "all metrics present")

    return data

def test_get_metrics(sim_id):
    """GET /simulations/{id}/metrics - Get metrics"""
    r = requests.get(f"{API}/simulations/{sim_id}/metrics")
    ok = r.status_code == 200
    data = r.json() if ok else {}
    log(ok, f"/simulations/{sim_id[:8]}../metrics", "GET",
        f"stability={data.get('stability_score','?')} risk={data.get('risk_level','?')}")

def test_get_allocations(sim_id, timestep=None):
    """GET /simulations/{id}/allocations - Get allocations"""
    url = f"{API}/simulations/{sim_id}/allocations"
    if timestep is not None:
        url += f"?timestep={timestep}"
    r = requests.get(url)
    ok = r.status_code == 200 and isinstance(r.json(), list)
    count = len(r.json()) if ok else 0
    log(ok, f"/simulations/{sim_id[:8]}../allocations", "GET",
        f"{'ts='+str(timestep)+' ' if timestep else ''}count={count}")

def test_get_events(sim_id):
    """GET /events/ - Get events for simulation"""
    r = requests.get(f"{API}/events/", params={"simulation_id": sim_id})
    ok = r.status_code == 200 and isinstance(r.json(), list)
    count = len(r.json()) if ok else 0
    log(ok, f"/events/?sim={sim_id[:8]}...", "GET", f"count={count}")

def test_get_timestep_logs(sim_id):
    """GET /timestep-logs/ - Get timestep logs"""
    r = requests.get(f"{API}/timestep-logs/", params={"simulation_id": sim_id})
    ok = r.status_code == 200 and isinstance(r.json(), list)
    count = len(r.json()) if ok else 0
    log(ok, f"/timestep-logs/?sim={sim_id[:8]}...", "GET", f"count={count}")

def test_delete_simulation(sim_id):
    """DELETE /simulations/{id} - Delete a simulation"""
    r = requests.delete(f"{API}/simulations/{sim_id}")
    ok = r.status_code == 200
    log(ok, f"/simulations/{sim_id[:8]}...", "DELETE", f"status={r.status_code}")

def test_step_on_completed(sim_id):
    """POST /simulations/{id}/step after completion - should return 400"""
    r = requests.post(f"{API}/simulations/{sim_id}/step")
    log(r.status_code == 400, f"/simulations/{sim_id[:8]}../step (completed)", "POST",
        f"status={r.status_code} (expect 400)")


# ── SCENARIO DEFINITIONS ──────────────────────────────────────────────────────
SCENARIOS = {
    "default": {
        "name": "Default Crisis",
        "timesteps": 5,
        "agents": [
            {"type": "hospital",  "name": "Central Hospital",   "demand": 180, "max": 200, "min": 100, "priority": 2.0},
            {"type": "power",     "name": "Power Grid Alpha",   "demand": 350, "max": 500, "min": 200, "priority": 1.8},
            {"type": "water",     "name": "Water Authority",    "demand": 250, "max": 350, "min": 150, "priority": 1.7},
            {"type": "emergency", "name": "Emergency Services", "demand": 120, "max": 150, "min": 80,  "priority": 1.9},
        ],
    },
    "earthquake": {
        "name": "Earthquake Recovery",
        "timesteps": 5,
        "agents": [
            {"type": "hospital",  "name": "Trauma Center A",  "demand": 198, "max": 250, "min": 150, "priority": 2.8},
            {"type": "hospital",  "name": "Trauma Center B",  "demand": 190, "max": 250, "min": 150, "priority": 2.6},
            {"type": "emergency", "name": "Search & Rescue",  "demand": 178, "max": 200, "min": 120, "priority": 2.5},
            {"type": "power",     "name": "City Power Grid",  "demand": 550, "max": 700, "min": 300, "priority": 1.5},
            {"type": "water",     "name": "Water Treatment",  "demand": 300, "max": 400, "min": 200, "priority": 1.7},
        ],
    },
    "flood": {
        "name": "Flood Response",
        "timesteps": 5,
        "agents": [
            {"type": "hospital",  "name": "Riverside Hospital", "demand": 195, "max": 250, "min": 150, "priority": 2.5},
            {"type": "water",     "name": "Flood Control",      "demand": 480, "max": 600, "min": 250, "priority": 2.2},
            {"type": "emergency", "name": "Rescue Operations",  "demand": 175, "max": 200, "min": 120, "priority": 2.4},
            {"type": "power",     "name": "Backup Generators",  "demand": 280, "max": 400, "min": 180, "priority": 1.6},
        ],
    },
}

def run_full_scenario(scenario_key, scenario):
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario['name']} ({scenario_key})")
    print(f"{'='*70}")

    # 1. Create simulation
    print("\n--- Create Simulation ---")
    sim_id = test_create_simulation(scenario["name"], scenario["timesteps"])
    if not sim_id:
        print("  SKIP: Cannot proceed without simulation ID")
        return

    # 2. Get simulation
    print("\n--- Get Simulation ---")
    test_get_simulation(sim_id)

    # 3. Add agents
    print(f"\n--- Add {len(scenario['agents'])} Agents ---")
    for ag in scenario["agents"]:
        test_add_agent(sim_id, ag["type"], ag["name"], ag["demand"], ag["max"], ag["min"], ag["priority"])

    # 4. Verify agents
    print("\n--- Verify Agents ---")
    test_get_agents(sim_id, expected_count=len(scenario["agents"]))

    # 5. Run steps
    print(f"\n--- Execute {scenario['timesteps']} Steps ---")
    for i in range(1, scenario["timesteps"] + 1):
        test_step(sim_id, i)

    # 6. Check metrics after steps
    print("\n--- Get Metrics ---")
    test_get_metrics(sim_id)

    # 7. Get allocations
    print("\n--- Get Allocations ---")
    test_get_allocations(sim_id)
    test_get_allocations(sim_id, timestep=1)

    # 8. Get events
    print("\n--- Get Events ---")
    test_get_events(sim_id)

    # 9. Get timestep logs
    print("\n--- Get Timestep Logs ---")
    test_get_timestep_logs(sim_id)

    # 10. Step on completed simulation
    print("\n--- Step on Completed Simulation ---")
    test_step_on_completed(sim_id)

    # 11. Delete simulation
    print("\n--- Delete Simulation ---")
    test_delete_simulation(sim_id)

    # 12. Verify deletion
    print("\n--- Verify Deletion (expect 404) ---")
    r = requests.get(f"{API}/simulations/{sim_id}")
    log(r.status_code == 404, f"/simulations/{sim_id[:8]}... (deleted)", "GET",
        f"status={r.status_code} (expect 404)")


def main():
    global PASS, FAIL
    print("=" * 70)
    print("CrisisGrid API - Comprehensive Route Testing")
    print("=" * 70)

    # Health check
    test_health()

    # Test 404 for non-existent simulation
    print("\n--- Edge Cases ---")
    test_get_simulation_404()

    # List existing simulations
    print("\n--- List Existing Simulations ---")
    test_list_simulations()

    # Run all scenarios
    for key, scenario in SCENARIOS.items():
        run_full_scenario(key, scenario)

    # Final summary
    print(f"\n{'='*70}")
    print(f"RESULTS: {PASS} passed, {FAIL} failed, {PASS+FAIL} total")
    print(f"{'='*70}")

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
