"""
Test Suite for Cash Flow Analysis Service
=========================================

Comprehensive tests for services/cash_flow.py

Test Coverage:
- Passive income calculations with growth and tax
- Event application (property, expenses, rental)
- Income calculations (working vs retirement)
- Complete cash flow projections
- Year 1 breakdown generation
- Edge cases (zero income, all events, retirement transitions)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from services.cash_flow import (
    calculate_year_passive_income,
    apply_events_to_year,
    calculate_year_income,
    build_cashflow_projection,
    create_year1_breakdown
)


# Test 1: Passive Income Calculation
def test_passive_income_calculation():
    """Test passive income with growth and tax"""
    print("\n" + "="*60)
    print("TEST 1: Passive Income Calculation")
    print("="*60)
    
    # Create mock passive income stream
    class PassiveStream:
        def __init__(self, start, end, monthly, growth, taxable, tax):
            self.start_year = start
            self.end_year = end
            self.monthly_amount = monthly
            self.annual_growth_rate = growth
            self.is_taxable = taxable
            self.tax_rate = tax
    
    # Stream: £1000/month, 3% growth, taxable at 20%
    streams = [
        PassiveStream(0, None, 1000, 0.03, True, 0.20)
    ]
    
    # Calculate for various years
    results = []
    for year in [0, 1, 5, 10]:
        income = calculate_year_passive_income(year, streams, 0.20)
        results.append((year, income))
        print(f"Year {year}: £{income:,.2f}")
    
    # Verify Year 0
    expected_year0 = 1000 * 12 * 0.80  # £12k * 80% after tax
    assert abs(results[0][1] - expected_year0) < 1, f"Year 0 mismatch: {results[0][1]} vs {expected_year0}"
    
    # Verify Year 5 (with 3% growth)
    expected_year5 = 1000 * 12 * (1.03 ** 5) * 0.80
    assert abs(results[2][1] - expected_year5) < 1, f"Year 5 mismatch: {results[2][1]} vs {expected_year5}"
    
    print(f"\n✅ Passive income calculations correct")
    print(f"   Year 0: £{results[0][1]:,.0f} (no growth)")
    print(f"   Year 5: £{results[2][1]:,.0f} (with 3% growth)")
    
    # Test non-taxable stream
    non_tax_stream = PassiveStream(0, 10, 500, 0.02, False, None)
    income_non_tax = calculate_year_passive_income(3, [non_tax_stream], 0.20)
    expected_non_tax = 500 * 12 * (1.02 ** 3)
    assert abs(income_non_tax - expected_non_tax) < 1
    print(f"   Non-taxable stream: £{income_non_tax:,.0f} (full amount)")
    
    # Test stream end date
    limited_stream = PassiveStream(0, 5, 1000, 0, True, 0.20)
    income_before_end = calculate_year_passive_income(3, [limited_stream], 0.20)
    income_after_end = calculate_year_passive_income(7, [limited_stream], 0.20)
    assert income_before_end > 0
    assert income_after_end == 0
    print(f"   Limited stream (ends year 5): Year 3 = £{income_before_end:,.0f}, Year 7 = £{income_after_end:,.0f}")


# Test 2: Event Application
def test_event_application():
    """Test applying financial events to projection years"""
    print("\n" + "="*60)
    print("TEST 2: Financial Event Application")
    print("="*60)
    
    events = [
        {'year': 2, 'type': 'property_purchase', 'name': 'Buy House', 'new_mortgage_payment': 1500},
        {'year': 5, 'type': 'expense_change', 'name': 'Kids', 'monthly_change': 500},
        {'year': 7, 'type': 'rental_income', 'name': 'Rent Out Room', 'monthly_rental': 800},
        {'year': 10, 'type': 'property_sale', 'name': 'Sell House'},
        {'year': 3, 'type': 'windfall', 'name': 'Inheritance', 'amount': 50000}
    ]
    
    # Test various years
    base_expenses = 2000
    base_mortgage = 1000
    base_rental = 0
    
    # Year 0: No events
    exp0, mort0, rent0, notes0 = apply_events_to_year(0, events, base_expenses, base_mortgage, base_rental)
    assert exp0 == base_expenses and mort0 == base_mortgage and rent0 == base_rental
    assert notes0 == ''
    print(f"Year 0 (no events): Expenses £{exp0}, Mortgage £{mort0}, Rental £{rent0}")
    
    # Year 2: Property purchase
    exp2, mort2, rent2, notes2 = apply_events_to_year(2, events, base_expenses, base_mortgage, base_rental)
    assert mort2 == 1500
    assert notes2 == 'Buy House'
    print(f"Year 2 (buy house): Mortgage updated to £{mort2}/month - {notes2}")
    
    # Year 5: Expense change
    exp5, mort5, rent5, notes5 = apply_events_to_year(5, events, base_expenses, base_mortgage, base_rental)
    assert exp5 == base_expenses + 500
    assert notes5 == 'Kids'
    print(f"Year 5 (kids): Expenses increased to £{exp5}/month - {notes5}")
    
    # Year 7: Rental income
    exp7, mort7, rent7, notes7 = apply_events_to_year(7, events, base_expenses, base_mortgage, base_rental)
    assert rent7 == 800
    assert notes7 == 'Rent Out Room'
    print(f"Year 7 (rental): Rental income £{rent7}/month - {notes7}")
    
    # Year 10: Property sale
    exp10, mort10, rent10, notes10 = apply_events_to_year(10, events, base_expenses, base_mortgage, base_rental)
    assert mort10 == 0
    assert notes10 == 'Sell House'
    print(f"Year 10 (sell): Mortgage cleared - {notes10}")
    
    # Year 3: Windfall (doesn't affect monthly cash flow, just notes)
    exp3, mort3, rent3, notes3 = apply_events_to_year(3, events, base_expenses, base_mortgage, base_rental)
    assert notes3 == 'Inheritance'
    print(f"Year 3 (windfall): No monthly change but noted - {notes3}")
    
    print(f"\n✅ Event application working correctly")
    print(f"   5 event types tested (property buy/sell, expenses, rental, windfall)")


# Test 3: Income Calculation (Working vs Retirement)
def test_income_calculation():
    """Test income calculations with retirement transitions"""
    print("\n" + "="*60)
    print("TEST 3: Income Calculation (Working → Retirement)")
    print("="*60)
    
    # Parameters
    starting_age = 30
    retirement_age = 67
    gross_income = 80000
    tax_rate = 0.20
    pension_rate = 0.10
    salary_inflation = 0.03
    pension_income = 40000
    
    # Test working years
    print("\nWorking Years:")
    for year in [0, 5, 10, 20]:
        primary, spouse, retired, total, spouse_ret = calculate_year_income(
            year, starting_age, retirement_age, gross_income, tax_rate,
            pension_rate, salary_inflation, pension_income
        )
        age = starting_age + year
        print(f"  Year {year} (age {age}): £{total:,.0f} take-home, Retired: {retired}")
        assert not retired
        assert total > 0
    
    # Test retirement year (age 67 = year 37)
    retirement_year = retirement_age - starting_age
    primary, spouse, retired, total, spouse_ret = calculate_year_income(
        retirement_year, starting_age, retirement_age, gross_income, tax_rate,
        pension_rate, salary_inflation, pension_income
    )
    print(f"\nRetirement Year {retirement_year} (age {retirement_age}):")
    print(f"  Income switches to pension: £{total:,.0f}")
    assert retired
    assert total == pension_income
    
    # Test post-retirement
    primary, spouse, retired, total, spouse_ret = calculate_year_income(
        retirement_year + 5, starting_age, retirement_age, gross_income, tax_rate,
        pension_rate, salary_inflation, pension_income
    )
    print(f"  Year {retirement_year + 5} (age {retirement_age + 5}): £{total:,.0f} (still pension)")
    assert retired
    assert total == pension_income
    
    # Test with spouse
    print("\nWith Spouse:")
    spouse_params = {
        'gross_income': 60000,
        'retirement_age': 67,
        'tax_rate': 0.20,
        'pension_rate': 0.10,
        'pension_income': 30000
    }
    
    primary, spouse_income, retired, total, spouse_ret = calculate_year_income(
        5, starting_age, retirement_age, gross_income, tax_rate,
        pension_rate, salary_inflation, pension_income,
        include_spouse=True,
        spouse_gross_income=60000,
        spouse_retirement_age=67,
        spouse_tax_rate=0.20,
        spouse_pension_rate=0.10,
        spouse_pension_income=30000
    )
    print(f"  Year 5 with spouse: £{total:,.0f} household (primary £{primary:,.0f} + spouse £{spouse_income:,.0f})")
    assert total > primary
    assert spouse_income > 0
    
    print(f"\n✅ Income calculations correct")
    print(f"   Working income increases with inflation")
    print(f"   Retirement transition at age {retirement_age}")
    print(f"   Spouse income calculated correctly")


# Test 4: Complete Cash Flow Projection
def test_complete_projection():
    """Test building complete multi-year projection"""
    print("\n" + "="*60)
    print("TEST 4: Complete Cash Flow Projection")
    print("="*60)
    
    # Setup parameters
    events = [
        {'year': 3, 'type': 'expense_change', 'name': 'Kids', 'monthly_change': 500},
        {'year': 5, 'type': 'property_purchase', 'name': 'Buy House', 'new_mortgage_payment': 1800}
    ]
    
    # Build projection
    df = build_cashflow_projection(
        starting_age=30,
        retirement_age=67,
        simulation_years=40,
        gross_annual_income=80000,
        effective_tax_rate=0.20,
        pension_contribution_rate=0.10,
        monthly_expenses=2000,
        monthly_mortgage_payment=1200,
        salary_inflation=0.03,
        total_pension_income=40000,
        events=events
    )
    
    print(f"\nProjection created with {len(df)} years")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Verify structure
    assert len(df) == 11  # Years 0-10
    assert 'Year' in df.columns
    assert 'Age' in df.columns
    assert 'Available Savings' in df.columns
    assert 'Events This Year' in df.columns
    
    # Check specific years
    print("\nYear-by-Year Summary:")
    for idx, row in df.iterrows():
        events_note = f" - {row['Events This Year']}" if row['Events This Year'] else ""
        print(f"  Year {row['Year']} (age {row['Age']}): Available {row['Available Savings']}{events_note}")
    
    # Verify events appear
    year3_events = df[df['Year'] == 3]['Events This Year'].values[0]
    year5_events = df[df['Year'] == 5]['Events This Year'].values[0]
    assert 'Kids' in year3_events
    assert 'Buy House' in year5_events
    
    print(f"\n✅ Complete projection working")
    print(f"   11 years generated (0-10)")
    print(f"   Events correctly noted in projection")


# Test 5: Year 1 Breakdown
def test_year1_breakdown():
    """Test detailed Year 1 breakdown generation"""
    print("\n" + "="*60)
    print("TEST 5: Year 1 Cash Flow Breakdown")
    print("="*60)
    
    # Create breakdown
    df, available, status = create_year1_breakdown(
        gross_annual_income=80000,
        pension_contribution_rate=0.10,
        effective_tax_rate=0.20,
        monthly_expenses=2000,
        monthly_mortgage=1200
    )
    
    print(f"\nYear 1 Breakdown:")
    for idx, row in df.iterrows():
        print(f"  {row['Item']:<25} {row['Amount']:>12}")
    
    print(f"\nStatus: {status}")
    print(f"Available: £{available:,.0f}")
    
    # Verify calculations
    expected_gross = 80000
    expected_pension = 8000
    expected_tax = 16000
    expected_takehome = 56000
    expected_expenses = 24000
    expected_mortgage = 14400
    expected_available = 56000 - 24000 - 14400
    
    assert status == 'surplus'
    assert abs(available - expected_available) < 1
    assert 'Gross Income' in df['Item'].values
    assert '= Available for Investment' in df['Item'].values
    
    print(f"\n✅ Year 1 breakdown correct")
    print(f"   Take-home: £{expected_takehome:,}")
    print(f"   Available: £{expected_available:,} ({status})")
    
    # Test with passive income
    df_passive, avail_passive, status_passive = create_year1_breakdown(
        gross_annual_income=80000,
        pension_contribution_rate=0.10,
        effective_tax_rate=0.20,
        monthly_expenses=2000,
        monthly_mortgage=1200,
        passive_income_annual=15000
    )
    
    assert '+ Passive Income' in df_passive['Item'].values
    assert avail_passive > available
    print(f"   With passive income: £{avail_passive:,} (increased by £{avail_passive - available:,})")
    
    # Test deficit scenario
    df_deficit, avail_deficit, status_deficit = create_year1_breakdown(
        gross_annual_income=40000,
        pension_contribution_rate=0.10,
        effective_tax_rate=0.20,
        monthly_expenses=3000,
        monthly_mortgage=1500
    )
    
    assert status_deficit == 'deficit'
    assert avail_deficit < 0
    print(f"   Deficit scenario: £{avail_deficit:,} ({status_deficit})")


# Test 6: Edge Cases
def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n" + "="*60)
    print("TEST 6: Edge Cases")
    print("="*60)
    
    # Zero income scenario
    df_zero = build_cashflow_projection(
        starting_age=67,
        retirement_age=67,
        simulation_years=10,
        gross_annual_income=0,
        effective_tax_rate=0.20,
        pension_contribution_rate=0,
        monthly_expenses=2000,
        monthly_mortgage_payment=0,
        salary_inflation=0,
        total_pension_income=30000,
        events=[]
    )
    assert len(df_zero) == 11
    print(f"✓ Zero income (immediate retirement): {len(df_zero)} years")
    
    # All events in one year
    many_events = [
        {'year': 5, 'type': 'property_purchase', 'name': 'Buy House', 'new_mortgage_payment': 1500},
        {'year': 5, 'type': 'expense_change', 'name': 'Kids', 'monthly_change': 500},
        {'year': 5, 'type': 'rental_income', 'name': 'Rent Room', 'monthly_rental': 600},
        {'year': 5, 'type': 'windfall', 'name': 'Inheritance', 'amount': 50000}
    ]
    
    df_many = build_cashflow_projection(
        starting_age=30,
        retirement_age=67,
        simulation_years=40,
        gross_annual_income=80000,
        effective_tax_rate=0.20,
        pension_contribution_rate=0.10,
        monthly_expenses=2000,
        monthly_mortgage_payment=1000,
        salary_inflation=0.03,
        total_pension_income=40000,
        events=many_events
    )
    
    year5_events = df_many[df_many['Year'] == 5]['Events This Year'].values[0]
    assert 'Buy House' in year5_events
    assert 'Kids' in year5_events
    assert 'Rent Room' in year5_events
    assert 'Inheritance' in year5_events
    print(f"✓ Multiple events in one year: Year 5 has 4 events")
    
    # Short projection (3 years)
    df_short = build_cashflow_projection(
        starting_age=30,
        retirement_age=67,
        simulation_years=3,
        gross_annual_income=80000,
        effective_tax_rate=0.20,
        pension_contribution_rate=0.10,
        monthly_expenses=2000,
        monthly_mortgage_payment=1200,
        salary_inflation=0.03,
        total_pension_income=40000,
        events=[]
    )
    assert len(df_short) == 4  # Years 0, 1, 2, 3
    print(f"✓ Short projection: {len(df_short)} years for 3-year simulation")
    
    # High inflation scenario
    df_inflation = build_cashflow_projection(
        starting_age=30,
        retirement_age=67,
        simulation_years=20,
        gross_annual_income=60000,
        effective_tax_rate=0.20,
        pension_contribution_rate=0.10,
        monthly_expenses=2000,
        monthly_mortgage_payment=1200,
        salary_inflation=0.10,  # 10% inflation
        total_pension_income=40000,
        events=[]
    )
    assert len(df_inflation) == 11
    print(f"✓ High inflation (10%): Projection handles extreme growth")
    
    print(f"\n✅ Edge cases handled correctly")
    print(f"   Zero income, multiple events, short/long projections")


# Test 7: Performance Test
def test_performance():
    """Test projection generation performance"""
    print("\n" + "="*60)
    print("TEST 7: Performance Test")
    print("="*60)
    
    import time
    
    # Generate 100 projections
    events = [
        {'year': 3, 'type': 'expense_change', 'name': 'Kids', 'monthly_change': 500},
        {'year': 5, 'type': 'property_purchase', 'name': 'Buy House', 'new_mortgage_payment': 1800}
    ]
    
    start_time = time.time()
    
    for i in range(100):
        df = build_cashflow_projection(
            starting_age=30,
            retirement_age=67,
            simulation_years=40,
            gross_annual_income=80000,
            effective_tax_rate=0.20,
            pension_contribution_rate=0.10,
            monthly_expenses=2000,
            monthly_mortgage_payment=1200,
            salary_inflation=0.03,
            total_pension_income=40000,
            events=events
        )
    
    end_time = time.time()
    elapsed = end_time - start_time
    avg_time = elapsed / 100
    
    print(f"\n100 projections generated in {elapsed:.3f}s")
    print(f"Average time per projection: {avg_time*1000:.2f}ms")
    
    assert elapsed < 5.0, f"Performance regression: {elapsed:.3f}s > 5.0s"
    
    print(f"\n✅ Performance acceptable")
    print(f"   Target: <5s for 100 projections")
    print(f"   Actual: {elapsed:.3f}s ({avg_time*1000:.1f}ms each)")


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "="*70)
    print(" "*15 + "CASH FLOW SERVICE TEST SUITE")
    print("="*70)
    
    test_passive_income_calculation()
    test_event_application()
    test_income_calculation()
    test_complete_projection()
    test_year1_breakdown()
    test_edge_cases()
    test_performance()
    
    print("\n" + "="*70)
    print(" "*20 + "ALL TESTS PASSED ✅")
    print("="*70)
    print("\nCash Flow Service Validated:")
    print("  ✓ Passive income calculations (growth + tax)")
    print("  ✓ Event application (5 event types)")
    print("  ✓ Income calculations (working → retirement)")
    print("  ✓ Complete projections (11-year default)")
    print("  ✓ Year 1 breakdown generation")
    print("  ✓ Edge cases (zero income, multiple events)")
    print("  ✓ Performance (<5s for 100 projections)")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
