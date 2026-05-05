"""MongoDB connection and client management for CrisisGrid"""

from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """Manages MongoDB connection and client lifecycle"""

    _instance: Optional[MongoClient] = None
    _db = None

    @classmethod
    def connect(cls) -> MongoClient:
        """
        Establish MongoDB connection.
        
        Returns singleton MongoDB client instance.
        Raises ConnectionFailure if unable to connect.
        """
        if cls._instance is not None:
            return cls._instance

        try:
            # Get MongoDB URI from settings (default: mongodb://localhost:27017)
            mongo_uri = getattr(settings, 'mongodb_url', 'mongodb://localhost:27017')
            
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                retryWrites=True,
                w='majority'  # Require write acknowledgment from majority
            )

            # Test connection
            client.admin.command('ping')
            logger.info("✓ Successfully connected to MongoDB")

            cls._instance = client
            return client

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"✗ Failed to connect to MongoDB: {str(e)}")
            raise

    @classmethod
    def get_client(cls) -> MongoClient:
        """Get MongoDB client (connects if not already connected)"""
        if cls._instance is None:
            cls.connect()
        return cls._instance

    @classmethod
    def get_database(cls):
        """Get CrisisGrid database instance"""
        if cls._db is None:
            client = cls.get_client()
            cls._db = client[getattr(settings, 'mongodb_database', 'crisisgrid')]
        return cls._db

    @classmethod
    def disconnect(cls):
        """Close MongoDB connection"""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            cls._db = None
            logger.info("✓ Disconnected from MongoDB")

    @classmethod
    def get_session(cls):
        """
        Get a MongoDB session for multi-document transactions.
        
        Returns a session that can be used for atomic operations.
        """
        client = cls.get_client()
        return client.start_session()


class MongoDBInitializer:
    """Initialize MongoDB collections and indexes"""

    @staticmethod
    def initialize_collections(db) -> dict:
        """
        Create all required collections if they don't exist.
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Dictionary with initialization results
        """
        from app.mongo_db.schemas import (
            SIMULATIONS_SCHEMA,
            AGENTS_SCHEMA,
            ALLOCATIONS_SCHEMA,
            EVENTS_SCHEMA,
            TIMESTEP_LOGS_SCHEMA,
            SYSTEM_STATE_SCHEMA
        )

        collections = {
            'simulations': SIMULATIONS_SCHEMA,
            'agents': AGENTS_SCHEMA,
            'allocations': ALLOCATIONS_SCHEMA,
            'events': EVENTS_SCHEMA,
            'timestep_logs': TIMESTEP_LOGS_SCHEMA,
            'system_state': SYSTEM_STATE_SCHEMA
        }

        results = {}

        for collection_name, schema in collections.items():
            try:
                # Check if collection exists
                if collection_name in db.list_collection_names():
                    logger.info(f"✓ Collection '{collection_name}' already exists")
                    results[collection_name] = 'exists'
                else:
                    # Create collection with validation schema
                    db.create_collection(
                        collection_name,
                        validator=schema
                    )
                    logger.info(f"✓ Created collection '{collection_name}'")
                    results[collection_name] = 'created'

            except Exception as e:
                logger.error(f"✗ Error creating collection '{collection_name}': {str(e)}")
                results[collection_name] = f'error: {str(e)}'

        return results

    @staticmethod
    def create_indexes(db) -> dict:
        """
        Create indexes for optimal query performance.
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Dictionary with index creation results
        """
        index_specs = {
            'simulations': [
                {'keys': [('created_at', -1)], 'name': 'idx_created_at'},
                {'keys': [('is_completed', 1)], 'name': 'idx_is_completed'},
            ],
            'agents': [
                {'keys': [('simulation_id', 1)], 'name': 'idx_simulation_id'},
                {'keys': [('trust_score', -1)], 'name': 'idx_trust_score'},
                {'keys': [('simulation_id', 1), ('agent_type', 1)], 'name': 'idx_sim_type'},
            ],
            'allocations': [
                {'keys': [('simulation_id', 1), ('timestep', 1)], 'name': 'idx_sim_timestep'},
                {'keys': [('agent_id', 1), ('resource_type', 1)], 'name': 'idx_agent_resource'},
                {'keys': [('resource_type', 1)], 'name': 'idx_resource_type'},
            ],
            'events': [
                {'keys': [('simulation_id', 1), ('timestep', 1)], 'name': 'idx_sim_timestep'},
                {'keys': [('event_type', 1)], 'name': 'idx_event_type'},
            ],
            'timestep_logs': [
                {'keys': [('simulation_id', 1), ('timestep', 1)], 'name': 'idx_sim_timestep'},
                {'keys': [('created_at', -1)], 'name': 'idx_created_at'},
            ],
            'system_state': [
                {'keys': [('simulation_id', 1)], 'name': 'idx_simulation_id'},
                {'keys': [('updated_at', -1)], 'name': 'idx_updated_at'},
            ],
        }

        results = {}

        for collection_name, indexes in index_specs.items():
            try:
                collection = db[collection_name]
                results[collection_name] = []

                for index_spec in indexes:
                    idx_name = collection.create_index(
                        index_spec['keys'],
                        name=index_spec['name']
                    )
                    logger.info(f"✓ Created index on '{collection_name}': {index_spec['name']}")
                    results[collection_name].append(index_spec['name'])

            except Exception as e:
                logger.error(f"✗ Error creating indexes for '{collection_name}': {str(e)}")
                results[collection_name] = f'error: {str(e)}'

        return results

    @staticmethod
    def initialize_all(db) -> dict:
        """
        Complete MongoDB initialization: collections + indexes.
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Dictionary with all initialization results
        """
        logger.info("Starting MongoDB initialization...")

        collections_result = MongoDBInitializer.initialize_collections(db)
        indexes_result = MongoDBInitializer.create_indexes(db)

        return {
            'collections': collections_result,
            'indexes': indexes_result
        }

    @staticmethod
    def verify_setup(db) -> dict:
        """
        Verify MongoDB is properly set up.
        
        Checks:
        - All collections exist
        - All indexes exist
        - Database is accessible
        
        Args:
            db: MongoDB database instance
            
        Returns:
            Dictionary with verification results
        """
        verification = {
            'database_accessible': False,
            'collections': {},
            'indexes': {},
            'status': 'unknown'
        }

        try:
            # Check database accessibility
            db.list_collection_names()
            verification['database_accessible'] = True

            # Check collections
            required_collections = [
                'simulations', 'agents', 'allocations', 'events', 'timestep_logs', 'system_state'
            ]
            existing_collections = db.list_collection_names()

            for coll in required_collections:
                verification['collections'][coll] = coll in existing_collections

            # Check indexes
            index_checks = {
                'simulations': ['idx_created_at', 'idx_is_completed'],
                'agents': ['idx_simulation_id', 'idx_trust_score', 'idx_sim_type'],
                'allocations': ['idx_sim_timestep', 'idx_agent_resource', 'idx_resource_type'],
                'events': ['idx_sim_timestep', 'idx_event_type'],
                'timestep_logs': ['idx_sim_timestep', 'idx_created_at'],
                'system_state': ['idx_simulation_id', 'idx_updated_at'],
            }

            for coll_name, required_indexes in index_checks.items():
                verification['indexes'][coll_name] = {}
                if coll_name in existing_collections:
                    collection = db[coll_name]
                    existing_indexes = [idx['name'] for idx in collection.list_indexes()]

                    for idx in required_indexes:
                        verification['indexes'][coll_name][idx] = idx in existing_indexes

            # Determine overall status
            all_collections_ok = all(verification['collections'].values())
            all_indexes_ok = all(
                all(idxs.values()) for idxs in verification['indexes'].values()
            )

            if verification['database_accessible'] and all_collections_ok and all_indexes_ok:
                verification['status'] = 'ready'
                logger.info("✓ MongoDB setup verified - all systems ready")
            else:
                verification['status'] = 'incomplete'
                logger.warning("⚠ MongoDB setup incomplete - missing collections or indexes")

        except Exception as e:
            verification['status'] = 'error'
            verification['error'] = str(e)
            logger.error(f"✗ MongoDB verification failed: {str(e)}")

        return verification


# Dependency: Get database for FastAPI
def get_mongodb() -> object:
    """FastAPI dependency to get MongoDB database instance"""
    return MongoDBConnection.get_database()
