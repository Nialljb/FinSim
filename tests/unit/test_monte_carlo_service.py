"""
Test suite for Monte Carlo simulation service
Verifies that the extracted service works correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from services.monte_carlo import run_monte_carlo, calculate_mortgage_payment


def test_calculate_mortgage_payment():
    """Test mortgage payment calculation"""
    print("\n" + "="*60)
    print("TEST 1: Mortgage Payment Calculation")
    print("="*60)
    
    # Test standard mortgage
    payment = calculate_mortgage_payment(300000, 0.035, 25)
    print(f"✓ £300,000 mortgage at 3.5% over 25 years = £{payment:,.2f}/month")
    assert payment > 1500 and payment < 1600, "Payment should be around £1,501"
    
    # Test zero principal
    payment = calculate_mortgage_payment(0, 0.035, 25)
    assert payment == 0, "Zero principal should give zero payment"
    print(f"✓ £0 mortgage = £{payment:.2f}/month")
    
    # Test zero interest
    payment = calculate_mortgage_payment(120000, 0, 10)
    assert payment == 1000, "Zero interest should give simple division"
    print(f"✓ £120,000 mortgage at 0% over 10 years = £{payment:,.2f}/month")
    
    print("✅ All mortgage payment tests passed!")


def test_monte_carlo_basic():
    """Test basic Monte Carlo simulation"""
    print("\n" + "="*60)
    print("TEST 2: Basic Monte Carlo Simulation")
    print("="*60)
    
    results = run_monte_carlo(
        initial_liquid_wealth=100000,
        initial_property_value=500000,
        initial_mortgage=400000,
        gross_annual_income=75000,
        effective_tax_rate=0.25,
        pension_contribution_rate=0.10,
        monthly_expenses=3000,
        monthly_mortgage_payment=2000,
        property_appreciation=0.03,
        mortgage_interest_rate=0.035,
        expected_return=0.07,
        return_volatility=0.15,
        expected_inflation=0.025,
        inflation_volatility=0.01,
        salary_inflation=0.025,
        years=10,
        n_simulations=100,
        events=[],
        random_seed=42
    )
    
    # Verify result structure
    assert 'net_worth' in results, "Results should contain net_worth"
    assert 'liquid_wealth' in results, "Results should contain liquid_wealth"
    assert 'pension_wealth' in results, "Results should contain pension_wealth"
    assert 'property_value' in results, "Results should contain property_value"
    assert 'mortgage_balance' in results, "Results should contain mortgage_balance"
    assert 'inflation_rates' in results, "Results should contain inflation_rates"
    print("✓ All required result keys present")
    
    # Verify dimensions
    assert results['net_worth'].shape == (100, 11), "Net worth should be (100 sims, 11 years)"
    assert results['inflation_rates'].shape == (100, 10), "Inflation should be (100 sims, 10 years)"
    print(f"✓ Result dimensions correct: {results['net_worth'].shape}")
    
    # Verify initial values
    initial_nw = results['net_worth'][:, 0]
    expected_initial = 100000 + 500000 - 400000  # 200,000
    assert np.allclose(initial_nw, expected_initial), "Initial net worth should match"
    print(f"✓ Initial net worth: £{np.mean(initial_nw):,.0f}")
    
    # Verify final values are reasonable
    final_nw = results['net_worth'][:, -1]
    median_final = np.median(final_nw)
    print(f"✓ Median final net worth (10 years): £{median_final:,.0f}")
    assert median_final > expected_initial, "Net worth should grow over time"
    
    print("✅ Basic Monte Carlo simulation test passed!")


def test_monte_carlo_with_retirement():
    """Test Monte Carlo with retirement transition"""
    print("\n" + "="*60)
    print("TEST 3: Monte Carlo with Retirement")
    print("="*60)
    
    results = run_monte_carlo(
        initial_liquid_wealth=500000,
        initial_property_value=600000,
        initial_mortgage=200000,
        gross_annual_income=100000,
        effective_tax_rate=0.30,
        pension_contribution_rate=0.12,
        monthly_expenses=4000,
        monthly_mortgage_payment=1500,
        property_appreciation=0.03,
        mortgage_interest_rate=0.03,
        expected_return=0.06,
        return_volatility=0.12,
        expected_inflation=0.02,
        inflation_volatility=0.005,
        salary_inflation=0.02,
        years=20,
        n_simulations=50,
        events=[],
        random_seed=123,
        starting_age=50,
        retirement_age=65,
        pension_income=40000  # Annual pension income
    )
    
    # Verify pension wealth accumulates pre-retirement (years 1-14)
    pension_year_14 = np.median(results['pension_wealth'][:, 14])
    pension_year_15 = np.median(results['pension_wealth'][:, 15])
    print(f"✓ Pension wealth at year 14 (age 64): £{pension_year_14:,.0f}")
    print(f"✓ Pension wealth at year 15 (age 65): £{pension_year_15:,.0f}")
    
    # Both should be positive
    assert pension_year_14 > 0, "Pension should accumulate pre-retirement"
    assert pension_year_15 > 0, "Pension should remain positive post-retirement"
    
    print("✅ Retirement transition test passed!")


def test_monte_carlo_with_events():
    """Test Monte Carlo with financial events"""
    print("\n" + "="*60)
    print("TEST 4: Monte Carlo with Financial Events")
    print("="*60)
    
    events = [
        {
            'type': 'windfall',
            'year': 2,
            'name': 'Inheritance',
            'amount': 100000
        },
        {
            'type': 'one_time_expense',
            'year': 5,
            'name': 'Home Renovation',
            'amount': 50000
        }
    ]
    
    results = run_monte_carlo(
        initial_liquid_wealth=100000,
        initial_property_value=400000,
        initial_mortgage=300000,
        gross_annual_income=80000,
        effective_tax_rate=0.25,
        pension_contribution_rate=0.10,
        monthly_expenses=3000,
        monthly_mortgage_payment=1800,
        property_appreciation=0.03,
        mortgage_interest_rate=0.035,
        expected_return=0.07,
        return_volatility=0.15,
        expected_inflation=0.025,
        inflation_volatility=0.01,
        salary_inflation=0.025,
        years=10,
        n_simulations=50,
        events=events,
        random_seed=42
    )
    
    # Check that liquid wealth increased at year 2 (windfall)
    liquid_year_1 = np.median(results['liquid_wealth'][:, 1])
    liquid_year_2 = np.median(results['liquid_wealth'][:, 2])
    print(f"✓ Liquid wealth year 1: £{liquid_year_1:,.0f}")
    print(f"✓ Liquid wealth year 2 (after windfall): £{liquid_year_2:,.0f}")
    
    # Year 2 should be higher than year 1 due to windfall
    assert liquid_year_2 > liquid_year_1, "Windfall should increase liquid wealth"
    
    print("✅ Financial events test passed!")


def test_mortgage_payment_edge_cases():
    """Test edge cases for mortgage calculation"""
    print("\n" + "="*60)
    print("TEST 5: Mortgage Payment Edge Cases")
    print("="*60)
    
    # Test zero years
    payment = calculate_mortgage_payment(100000, 0.035, 0)
    assert payment == 0, "Zero years should give zero payment"
    print(f"✓ Zero years: £{payment:.2f}")
    
    # Test negative values (should return 0)
    payment = calculate_mortgage_payment(-100000, 0.035, 25)
    assert payment == 0, "Negative principal should give zero payment"
    print(f"✓ Negative principal: £{payment:.2f}")
    
    # Test very high interest rate
    payment = calculate_mortgage_payment(100000, 0.20, 10)
    print(f"✓ High interest (20%): £{payment:,.2f}/month")
    assert payment > 0, "High interest should still calculate"
    
    print("✅ Edge case tests passed!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MONTE CARLO SERVICE EXTRACTION TEST SUITE")
    print("="*60)
    
    test_calculate_mortgage_payment()
    test_monte_carlo_basic()
    test_monte_carlo_with_retirement()
    test_monte_carlo_with_events()
    test_mortgage_payment_edge_cases()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n✨ Monte Carlo service extraction successful!")
    print("📦 Service can now be imported as: from services.monte_carlo import run_monte_carlo")
    print("🧪 All functionality verified and working correctly")
    print()
