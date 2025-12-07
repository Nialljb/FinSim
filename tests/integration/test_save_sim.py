#!/usr/bin/env python3
"""
Test the save_simulation function to identify the issue
"""

import numpy as np
from datetime import datetime
from test.database import SessionLocal, User, Simulation
from data_layer.data_tracking import save_simulation

def test_save():
    """Test saving a simulation"""
    
    # First, get a user to test with
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("❌ No users found. Create a user first.")
            return
        
        test_user = users[0]
        print(f"✅ Testing with user: {test_user.username} (ID: {test_user.id})")
        
    finally:
        db.close()
    
    # Create sample simulation parameters
    simulation_params = {
        'name': 'Test Simulation',
        'currency': 'USD',
        'initial_liquid_wealth': 100000,
        'initial_property_value': 250000,
        'initial_mortgage': 200000,
        'gross_annual_income': 80000,
        'monthly_expenses': 3000,
        'events': [
            {'type': 'property_purchase', 'name': 'Buy house', 'year': 5},
            {'type': 'expense_change', 'name': 'First child', 'year': 3}
        ],
        'expected_return': 0.07,
        'expected_inflation': 0.025,
        'simulation_years': 30,
        'starting_age': 30,
        'retirement_age': 60
    }
    
    # Create sample results (like what run_monte_carlo returns)
    n_simulations = 100
    years = 30
    
    results = {
        'net_worth': np.random.randn(n_simulations, years + 1) * 100000 + 500000,
        'real_net_worth': np.random.randn(n_simulations, years + 1) * 100000 + 500000,
        'liquid_wealth': np.random.randn(n_simulations, years + 1) * 50000 + 200000,
        'pension_wealth': np.random.randn(n_simulations, years + 1) * 30000 + 100000,
        'property_value': np.random.randn(n_simulations, years + 1) * 50000 + 300000,
        'mortgage_balance': np.random.randn(n_simulations, years + 1) * 20000 + 100000,
        'inflation_rates': np.random.randn(n_simulations, years) * 0.01 + 0.025
    }
    
    print("\n" + "="*80)
    print("📊 TEST DATA SUMMARY")
    print("="*80)
    print(f"Simulation params: {len(simulation_params)} fields")
    print(f"Results shape: net_worth = {results['net_worth'].shape}")
    print(f"Events: {len(simulation_params['events'])}")
    print("="*80)
    
    # Try to save
    print("\n🧪 Attempting to save simulation...")
    success, result = save_simulation(test_user.id, simulation_params, results)
    
    if success:
        print(f"✅ SUCCESS! Simulation saved with ID: {result}")
        
        # Verify it's in the database
        db = SessionLocal()
        try:
            sim = db.query(Simulation).filter(Simulation.id == result).first()
            if sim:
                print("\n📋 SAVED SIMULATION DETAILS:")
                print(f"  ID: {sim.id}")
                print(f"  Name: {sim.name}")
                print(f"  User ID: {sim.user_id}")
                print(f"  Currency: {sim.currency}")
                print(f"  Events: {sim.number_of_events}")
                print(f"  Has property purchase: {sim.has_property_purchase}")
                print(f"  Has children: {sim.has_children}")
                print(f"  Created: {sim.created_at}")
                
                # Check if parameters were saved
                if sim.parameters:
                    print(f"  Parameters saved: ✅ ({len(sim.parameters)} fields)")
                else:
                    print(f"  Parameters saved: ❌")
                
                print("\n✅ VERIFICATION SUCCESSFUL!")
            else:
                print(f"❌ ERROR: Simulation ID {result} not found in database!")
        finally:
            db.close()
            
    else:
        print(f"❌ FAILED to save simulation")
        print(f"Error: {result}")
        
        # Show the error in detail
        import traceback
        print("\n" + "="*80)
        print("ERROR DETAILS:")
        print("="*80)
        print(result)
        print("="*80)

if __name__ == "__main__":
    test_save()