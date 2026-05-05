"""Integration tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.models.base import Base
from app.database.session import get_db


# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestSimulationEndpoints:
    """Test simulation API endpoints"""

    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "CrisisGrid" in data["message"]

    def test_create_simulation(self):
        """Test creating a simulation"""
        response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Test Simulation",
                "description": "A test crisis response simulation",
                "total_timesteps": 100,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Simulation"
        assert data["total_timesteps"] == 100
        assert data["current_timestep"] == 0

    def test_list_simulations(self):
        """Test listing simulations"""
        # Create a simulation first
        client.post(
            "/api/v1/simulations/",
            json={
                "name": "Test Sim 1",
                "description": None,
                "total_timesteps": 50,
            },
        )

        response = client.get("/api/v1/simulations/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["name"] == "Test Sim 1"

    def test_get_simulation(self):
        """Test getting a specific simulation"""
        # Create a simulation
        create_response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Get Test Sim",
                "description": "For testing",
                "total_timesteps": 75,
            },
        )
        sim_id = create_response.json()["id"]

        # Get it
        response = client.get(f"/api/v1/simulations/{sim_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Get Test Sim"
        assert data["id"] == sim_id

    def test_add_agent_to_simulation(self):
        """Test adding an agent to a simulation"""
        # Create simulation
        sim_response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Agent Test Sim",
                "description": None,
                "total_timesteps": 100,
            },
        )
        sim_id = sim_response.json()["id"]

        # Add agent
        response = client.post(
            f"/api/v1/simulations/{sim_id}/agents",
            params={
                "agent_type": "hospital",
                "name": "Central Hospital",
                "current_demand": 80.0,
                "max_demand": 100.0,
                "min_demand": 50.0,
                "priority_level": 2.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Central Hospital"
        assert data["agent_type"] == "AgentType.HOSPITAL"

    def test_get_simulation_agents(self):
        """Test getting agents for a simulation"""
        # Create simulation and add agents
        sim_response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Multi Agent Sim",
                "description": None,
                "total_timesteps": 100,
            },
        )
        sim_id = sim_response.json()["id"]

        # Add multiple agents
        client.post(
            f"/api/v1/simulations/{sim_id}/agents",
            params={
                "agent_type": "hospital",
                "name": "Hospital",
                "current_demand": 80.0,
                "max_demand": 100.0,
                "min_demand": 50.0,
            },
        )

        client.post(
            f"/api/v1/simulations/{sim_id}/agents",
            params={
                "agent_type": "power",
                "name": "Power Grid",
                "current_demand": 200.0,
                "max_demand": 500.0,
                "min_demand": 100.0,
            },
        )

        # Get agents
        response = client.get(f"/api/v1/simulations/{sim_id}/agents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Hospital"
        assert data[1]["name"] == "Power Grid"

    def test_get_simulation_metrics(self):
        """Test getting simulation metrics"""
        # Create simulation
        sim_response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Metrics Test",
                "description": None,
                "total_timesteps": 100,
            },
        )
        sim_id = sim_response.json()["id"]

        # Get metrics
        response = client.get(f"/api/v1/simulations/{sim_id}/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "stability_score" in data
        assert "unmet_demand" in data
        assert "risk_level" in data
        assert "current_timestep" in data
        assert "progress" in data

    def test_simulation_not_found(self):
        """Test getting non-existent simulation"""
        response = client.get("/api/v1/simulations/9999")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_delete_simulation(self):
        """Test deleting a simulation"""
        # Create simulation
        sim_response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Delete Test",
                "description": None,
                "total_timesteps": 100,
            },
        )
        sim_id = sim_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/v1/simulations/{sim_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/v1/simulations/{sim_id}")
        assert response.status_code == 404


class TestSimulationExecution:
    """Test simulation execution through API"""

    def test_simulation_step_execution(self):
        """Test executing a simulation step"""
        # Create simulation
        sim_response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Step Test",
                "description": None,
                "total_timesteps": 100,
            },
        )
        sim_id = sim_response.json()["id"]

        # Add agents
        client.post(
            f"/api/v1/simulations/{sim_id}/agents",
            params={
                "agent_type": "hospital",
                "name": "Hospital",
                "current_demand": 80.0,
                "max_demand": 100.0,
                "min_demand": 50.0,
                "priority_level": 2.0,
            },
        )

        client.post(
            f"/api/v1/simulations/{sim_id}/agents",
            params={
                "agent_type": "power",
                "name": "Power",
                "current_demand": 200.0,
                "max_demand": 500.0,
                "min_demand": 100.0,
                "priority_level": 1.8,
            },
        )

        # Execute step
        response = client.post(f"/api/v1/simulations/{sim_id}/step")
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "state" in data
        assert "agents" in data
        assert "allocations" in data
        assert "bids" in data
        assert "metrics" in data
        assert "explanations" in data

        # Verify metrics
        metrics = data["metrics"]
        assert 0.0 <= metrics["stability_score"] <= 1.0
        assert metrics["unmet_demand"] >= 0
        assert 0.0 <= metrics["risk_level"] <= 1.0

        # Verify agents have allocations
        assert len(data["agents"]) == 2
        assert len(data["allocations"]) == 2

    def test_multiple_timesteps(self):
        """Test executing multiple timesteps"""
        # Create simulation
        sim_response = client.post(
            "/api/v1/simulations/",
            json={
                "name": "Multi-Step Test",
                "description": None,
                "total_timesteps": 100,
            },
        )
        sim_id = sim_response.json()["id"]

        # Add agent
        client.post(
            f"/api/v1/simulations/{sim_id}/agents",
            params={
                "agent_type": "emergency",
                "name": "Emergency Services",
                "current_demand": 60.0,
                "max_demand": 80.0,
                "min_demand": 40.0,
            },
        )

        # Execute multiple steps
        for step in range(3):
            response = client.post(f"/api/v1/simulations/{sim_id}/step")
            assert response.status_code == 200
            data = response.json()
            assert data["state"]["current_timestep"] == step

        # Verify final state
        response = client.get(f"/api/v1/simulations/{sim_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["current_timestep"] == 3
