"""MongoDB module for CrisisGrid data persistence"""

from app.mongo_db.connection import (
    MongoDBConnection,
    MongoDBInitializer,
    get_mongodb,
)
from app.mongo_db.repository import (
    SimulationRepository,
    AgentRepository,
    AllocationRepository,
    EventRepository,
    TimestepLogRepository,
    SystemStateRepository,
)
from app.mongo_db.analytics import AnalyticsRepository
from app.mongo_db.db_utils import (
    MongoDBTransactionManager,
    MongoDBConsistencyValidator,
    MongoDBOptimizer,
)

__all__ = [
    # Connection
    'MongoDBConnection',
    'MongoDBInitializer',
    'get_mongodb',
    # Repositories
    'SimulationRepository',
    'AgentRepository',
    'AllocationRepository',
    'EventRepository',
    'TimestepLogRepository',
    'SystemStateRepository',
    # Analytics
    'AnalyticsRepository',
    # Utilities
    'MongoDBTransactionManager',
    'MongoDBConsistencyValidator',
    'MongoDBOptimizer',
]
