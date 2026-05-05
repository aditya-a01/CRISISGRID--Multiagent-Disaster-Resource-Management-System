"""Configuration management for CrisisGrid"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database - SQLite (legacy)
    database_url: str = "sqlite:///./crisis_grid.db"

    # Database - MongoDB (recommended)
    mongodb_url: str = "mongodb+srv://adityaanil40_db_user:fb9JX769WZLFCW3d@cluster0.xpizjo3.mongodb.net/?appName=Cluster0"
    mongodb_database: str = "crisisgrid"
    use_mongodb: bool = True  # Set to True to use MongoDB instead of SQLite

    # API
    debug: bool = True
    api_version: str = "v1"
    api_title: str = "CrisisGrid Backend Engine"
    api_description: str = "Multi-agent crisis response system with autonomous negotiation"

    # Simulation
    simulation_tick_interval_ms: int = 1000
    default_simulation_duration_steps: int = 1000

    # Agent defaults
    default_agent_max_demand: float = 100.0
    default_agent_min_demand: float = 10.0
    default_trust_score_initial: float = 0.5

    # Constraints
    resource_power_total: float = 1000.0
    resource_water_total: float = 500.0
    min_hospital_power_allocation: float = 50.0
    min_hospital_water_allocation: float = 30.0

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
