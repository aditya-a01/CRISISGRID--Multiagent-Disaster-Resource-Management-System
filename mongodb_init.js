// MongoDB Initialization Script for CrisisGrid
// Run this in VS Code MongoDB extension or MongoDB Compass
// Database: crisisgrid

// ============================================================================
// Step 1: Switch to crisisgrid database
// ============================================================================
use('crisisgrid');

// ============================================================================
// Step 2: Create Collections with Validation Schemas
// ============================================================================

// Simulations Collection
db.createCollection('simulations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'total_timesteps', 'created_at'],
      properties: {
        _id: { bsonType: 'objectId' },
        name: { bsonType: 'string', minLength: 1, maxLength: 255 },
        description: { bsonType: 'string', maxLength: 1000 },
        current_timestep: { bsonType: 'int', minimum: 0 },
        total_timesteps: { bsonType: 'int', minimum: 1 },
        is_running: { bsonType: 'bool' },
        is_completed: { bsonType: 'bool' },
        power_available: { bsonType: 'double', minimum: 0 },
        water_available: { bsonType: 'double', minimum: 0 },
        stability_score: { bsonType: 'double', minimum: 0, maximum: 1 },
        unmet_demand: { bsonType: 'double', minimum: 0 },
        risk_level: { bsonType: 'double', minimum: 0, maximum: 1 },
        started_at: { bsonType: 'date' },
        completed_at: { bsonType: 'date' },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

print('✓ Created simulations collection');

// Agents Collection
db.createCollection('agents', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['simulation_id', 'agent_type', 'name', 'created_at'],
      properties: {
        _id: { bsonType: 'objectId' },
        simulation_id: { bsonType: 'objectId' },
        agent_type: { enum: ['hospital', 'water', 'power', 'emergency'] },
        name: { bsonType: 'string', minLength: 1, maxLength: 255 },
        current_demand: { bsonType: 'double', minimum: 0 },
        allocated_resources: { bsonType: 'double', minimum: 0 },
        max_demand: { bsonType: 'double', minimum: 0 },
        min_demand: { bsonType: 'double', minimum: 0 },
        priority_level: { bsonType: 'double', minimum: 0.5 },
        dependency_factor: { bsonType: 'double', minimum: 0, maximum: 1 },
        behavior_profile: { enum: ['cooperative', 'competitive', 'adaptive'] },
        risk_tolerance: { bsonType: 'double', minimum: 0, maximum: 1 },
        cooperation_level: { bsonType: 'double', minimum: 0, maximum: 1 },
        urgency_bias: { bsonType: 'double', minimum: 0, maximum: 1 },
        trust_score: { bsonType: 'double', minimum: 0, maximum: 1 },
        memory_log: { bsonType: 'array' },
        current_bid: { bsonType: 'double', minimum: 0 },
        unmet_demand: { bsonType: 'double', minimum: 0 },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

print('✓ Created agents collection');

// Allocations Collection
db.createCollection('allocations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['simulation_id', 'agent_id', 'timestep', 'created_at'],
      properties: {
        _id: { bsonType: 'objectId' },
        simulation_id: { bsonType: 'objectId' },
        agent_id: { bsonType: 'objectId' },
        timestep: { bsonType: 'int', minimum: 0 },
        resource_type: { enum: ['power', 'water'] },
        allocated_amount: { bsonType: 'double', minimum: 0 },
        requested_amount: { bsonType: 'double', minimum: 0 },
        utility_score: { bsonType: 'double' },
        was_fulfilled: { bsonType: 'double', minimum: 0, maximum: 1 },
        explanation: { bsonType: 'string', maxLength: 1000 },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

print('✓ Created allocations collection');

// Events Collection
db.createCollection('events', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['simulation_id', 'timestep', 'event_type', 'severity', 'created_at'],
      properties: {
        _id: { bsonType: 'objectId' },
        simulation_id: { bsonType: 'objectId' },
        timestep: { bsonType: 'int', minimum: 0 },
        event_type: { enum: ['power_outage', 'water_shortage', 'demand_spike', 'infrastructure_failure', 'recovery'] },
        severity: { bsonType: 'double', minimum: 0, maximum: 1 },
        affected_agent_type: { enum: ['hospital', 'water', 'power', 'emergency', null] },
        description: { bsonType: 'string', maxLength: 500 },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

print('✓ Created events collection');

// Timestep Logs Collection
db.createCollection('timestep_logs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['simulation_id', 'timestep', 'created_at'],
      properties: {
        _id: { bsonType: 'objectId' },
        simulation_id: { bsonType: 'objectId' },
        timestep: { bsonType: 'int', minimum: 0 },
        power_available: { bsonType: 'double', minimum: 0 },
        water_available: { bsonType: 'double', minimum: 0 },
        power_allocated: { bsonType: 'double', minimum: 0 },
        water_allocated: { bsonType: 'double', minimum: 0 },
        stability_score: { bsonType: 'double', minimum: 0, maximum: 1 },
        risk_level: { bsonType: 'double', minimum: 0, maximum: 1 },
        unmet_demand: { bsonType: 'double', minimum: 0 },
        allocation_efficiency: { bsonType: 'double', minimum: 0, maximum: 1 },
        fairness_score: { bsonType: 'double', minimum: 0, maximum: 1 },
        total_agents: { bsonType: 'int' },
        agents_satisfied: { bsonType: 'int' },
        agents_critical: { bsonType: 'int' },
        events_occurred: { bsonType: 'int' },
        events_summary: { bsonType: 'array' },
        total_bids: { bsonType: 'int' },
        avg_utility_score: { bsonType: 'double' },
        highest_utility_score: { bsonType: 'double' },
        avg_trust_score: { bsonType: 'double' },
        min_trust_score: { bsonType: 'double' },
        max_trust_score: { bsonType: 'double' },
        power_satisfaction_rate: { bsonType: 'double', minimum: 0, maximum: 1 },
        water_satisfaction_rate: { bsonType: 'double', minimum: 0, maximum: 1 },
        notes: { bsonType: 'string', maxLength: 1000 },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

print('✓ Created timestep_logs collection');

// System State Collection
db.createCollection('system_state', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['simulation_id', 'created_at'],
      properties: {
        _id: { bsonType: 'objectId' },
        simulation_id: { bsonType: 'objectId' },
        total_power: { bsonType: 'double', minimum: 0 },
        total_water: { bsonType: 'double', minimum: 0 },
        power_allocated: { bsonType: 'double', minimum: 0 },
        water_allocated: { bsonType: 'double', minimum: 0 },
        active_agents: { bsonType: 'int' },
        critical_agents: { bsonType: 'int' },
        stability: { bsonType: 'double', minimum: 0, maximum: 1 },
        risk: { bsonType: 'double', minimum: 0, maximum: 1 },
        unmet_demand: { bsonType: 'double', minimum: 0 },
        active_events: { bsonType: 'array' },
        created_at: { bsonType: 'date' },
        updated_at: { bsonType: 'date' }
      }
    }
  }
});

print('✓ Created system_state collection');

// ============================================================================
// Step 3: Create Indexes for Performance
// ============================================================================

// Simulations Indexes
db.simulations.createIndex({ created_at: -1 }, { name: 'idx_created_at' });
db.simulations.createIndex({ is_completed: 1 }, { name: 'idx_is_completed' });
print('✓ Created simulations indexes');

// Agents Indexes
db.agents.createIndex({ simulation_id: 1 }, { name: 'idx_simulation_id' });
db.agents.createIndex({ trust_score: -1 }, { name: 'idx_trust_score' });
db.agents.createIndex({ simulation_id: 1, agent_type: 1 }, { name: 'idx_sim_type' });
print('✓ Created agents indexes');

// Allocations Indexes
db.allocations.createIndex(
  { simulation_id: 1, timestep: 1 },
  { name: 'idx_sim_timestep' }
);
db.allocations.createIndex(
  { agent_id: 1, resource_type: 1 },
  { name: 'idx_agent_resource' }
);
db.allocations.createIndex({ resource_type: 1 }, { name: 'idx_resource_type' });
print('✓ Created allocations indexes');

// Events Indexes
db.events.createIndex(
  { simulation_id: 1, timestep: 1 },
  { name: 'idx_sim_timestep' }
);
db.events.createIndex({ event_type: 1 }, { name: 'idx_event_type' });
print('✓ Created events indexes');

// Timestep Logs Indexes
db.timestep_logs.createIndex(
  { simulation_id: 1, timestep: 1 },
  { name: 'idx_sim_timestep' }
);
db.timestep_logs.createIndex({ created_at: -1 }, { name: 'idx_created_at' });
print('✓ Created timestep_logs indexes');

// System State Indexes
db.system_state.createIndex({ simulation_id: 1 }, { name: 'idx_simulation_id' });
db.system_state.createIndex({ updated_at: -1 }, { name: 'idx_updated_at' });
print('✓ Created system_state indexes');

// ============================================================================
// Step 4: Verification
// ============================================================================

print('\n=== MongoDB Setup Complete ===');
print('Collections created: ' + db.getCollectionNames().length);
print('Collections: ' + db.getCollectionNames().join(', '));

// Show index information
print('\n=== Index Summary ===');
const collections = ['simulations', 'agents', 'allocations', 'events', 'timestep_logs', 'system_state'];

collections.forEach(collName => {
  const indexCount = db[collName].getIndexes().length - 1; // Exclude _id index
  print(`${collName}: ${indexCount} indexes`);
});

print('\n✓ MongoDB is ready for CrisisGrid!');
