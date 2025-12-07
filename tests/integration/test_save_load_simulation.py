"""
Test script for save/load simulation functionality
"""

from data_layer.data_tracking import save_full_simulation, load_simulation, get_user_simulations, delete_simulation, update_simulation_name
import numpy as np

# Test user ID (assuming user 1 exists)
test_user_id = 1

print("=" * 60)
print("Testing Save/Load Simulation Functionality")
print("=" * 60)

# Create a test simulation state
test_state = {
    'parameters': {
        'name': 'Test Simulation',
        'currency': 'CAD',
        'initial_liquid_wealth': 100000,
        'initial_property_value': 500000,
        'initial_mortgage': 300000,
        'gross_annual_income': 80000,
        'monthly_expenses': 4000,
        'events': [
            {
                'type': 'property_purchase',
                'year': 5,
                'name': 'Buy Investment Property',
                'property_price': 400000,
                'down_payment': 80000,
            }
        ],
        'starting_age': 35,
        'retirement_age': 65,
        'simulation_years': 30,
    },
    'results_data': {
        'net_worth': np.random.rand(100, 31).tolist(),  # Simulated results
        'liquid_wealth': np.random.rand(100, 31).tolist(),
    },
    'results': {
        'final_median_net_worth': 1500000,
        'probability_of_success': 0.85,
    }
}

# Test 1: Save simulation
print("\n1. Testing save_full_simulation...")
success, sim_id = save_full_simulation(test_user_id, "Test Simulation", test_state)
if success:
    print(f"   ✅ Successfully saved simulation with ID: {sim_id}")
else:
    print(f"   ❌ Failed to save: {sim_id}")
    exit(1)

# Test 2: Load simulation
print("\n2. Testing load_simulation...")
success, data = load_simulation(sim_id, test_user_id)
if success:
    print(f"   ✅ Successfully loaded simulation: {data['name']}")
    print(f"   - Created: {data['created_at']}")
    print(f"   - Currency: {data['state']['parameters']['currency']}")
    print(f"   - Initial Wealth: {data['state']['parameters']['initial_liquid_wealth']}")
else:
    print(f"   ❌ Failed to load: {data}")
    exit(1)

# Test 3: Get user simulations
print("\n3. Testing get_user_simulations...")
sims = get_user_simulations(test_user_id, limit=5)
print(f"   ✅ Found {len(sims)} simulation(s) for user {test_user_id}")
for sim in sims:
    print(f"   - {sim.name} (ID: {sim.id}, Created: {sim.created_at.strftime('%Y-%m-%d %H:%M')})")

# Test 4: Update simulation name
print("\n4. Testing update_simulation_name...")
new_name = "Renamed Test Simulation"
success, message = update_simulation_name(sim_id, test_user_id, new_name)
if success:
    print(f"   ✅ {message}")
    
    # Verify the name was updated
    success, data = load_simulation(sim_id, test_user_id)
    if data['name'] == new_name:
        print(f"   ✅ Verified: Name updated to '{new_name}'")
    else:
        print(f"   ❌ Name mismatch: expected '{new_name}', got '{data['name']}'")
else:
    print(f"   ❌ {message}")

# Test 5: Delete simulation
print("\n5. Testing delete_simulation...")
success, message = delete_simulation(sim_id, test_user_id)
if success:
    print(f"   ✅ {message}")
    
    # Verify it was deleted
    success, data = load_simulation(sim_id, test_user_id)
    if not success:
        print(f"   ✅ Verified: Simulation no longer accessible")
    else:
        print(f"   ❌ Simulation still accessible after deletion")
else:
    print(f"   ❌ {message}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
