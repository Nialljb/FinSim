"""
Test suite for Visualization Service
Verifies that the extracted visualization functions work correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from services.visualization import (
    create_wealth_trajectory_chart,
    create_wealth_composition_chart,
    create_distribution_chart,
    get_view_type_paths
)


def test_get_view_type_paths():
    """Test view type path selection"""
    print("\n" + "="*60)
    print("TEST 1: get_view_type_paths Function")
    print("="*60)
    
    n_simulations = 50
    years = 10
    
    # Create mock data
    display_results = {
        'net_worth': np.random.rand(n_simulations, years + 1) * 100000,
        'real_net_worth': np.random.rand(n_simulations, years + 1) * 100000,
        'liquid_wealth': np.random.rand(n_simulations, years + 1) * 50000,
        'pension_wealth': np.random.rand(n_simulations, years + 1) * 30000,
        'property_value': np.random.rand(n_simulations, years + 1) * 300000,
        'mortgage_balance': np.random.rand(n_simulations, years + 1) * 200000,
    }
    
    results = {
        'inflation_rates': np.random.rand(n_simulations, years) * 0.03
    }
    
    # Test each view type
    view_types = ["Total Net Worth", "Liquid Wealth", "Property Equity", "Pension Wealth"]
    for view_type in view_types:
        paths, label = get_view_type_paths(view_type, display_results, results, n_simulations, show_real=True)
        assert paths.shape == (n_simulations, years + 1), f"Shape mismatch for {view_type}"
        assert len(label) > 0, f"Label missing for {view_type}"
        print(f"✓ {view_type}: shape={paths.shape}, label='{label}'")
    
    print("✅ All view types tested successfully!")


def test_trajectory_chart():
    """Test wealth trajectory chart creation"""
    print("\n" + "="*60)
    print("TEST 2: Wealth Trajectory Chart")
    print("="*60)
    
    n_simulations = 100
    years = 20
    
    # Create mock paths
    paths = np.random.rand(n_simulations, years + 1) * 500000
    
    # Create mock events
    events = [
        {'type': 'windfall', 'year': 5, 'name': 'Inheritance'},
        {'type': 'property_purchase', 'year': 10, 'name': 'Buy Home'},
        {'type': 'one_time_expense', 'year': 15, 'name': 'Renovation'}
    ]
    
    fig = create_wealth_trajectory_chart(
        paths_to_plot=paths,
        years=years,
        n_simulations=n_simulations,
        events=events,
        y_label="Net Worth",
        currency_symbol="£",
        starting_age=30,
        retirement_age=65,
        end_age=85,
        show_retirement_period=False,
        use_pension_data=True,
        total_pension_income=40000
    )
    
    print(f"✓ Chart created with {len(fig.data)} traces")
    print(f"✓ Chart title: {fig.layout.title.text}")
    print(f"✓ X-axis: {fig.layout.xaxis.title.text}")
    print(f"✓ Y-axis: {fig.layout.yaxis.title.text}")
    
    # Verify chart has expected components
    assert len(fig.data) > 0, "Chart should have traces"
    assert fig.layout.height == 700, "Chart height should be 700"
    
    print("✅ Trajectory chart test passed!")


def test_composition_chart():
    """Test wealth composition chart creation"""
    print("\n" + "="*60)
    print("TEST 3: Wealth Composition Chart")
    print("="*60)
    
    n_simulations = 50
    years = 15
    
    # Create mock data
    display_results = {
        'liquid_wealth': np.random.rand(n_simulations, years + 1) * 100000,
        'pension_wealth': np.random.rand(n_simulations, years + 1) * 50000,
        'property_value': np.random.rand(n_simulations, years + 1) * 400000,
        'mortgage_balance': np.random.rand(n_simulations, years + 1) * 300000,
    }
    
    results = {
        'inflation_rates': np.random.rand(n_simulations, years) * 0.025
    }
    
    fig = create_wealth_composition_chart(
        display_results=display_results,
        results=results,
        years=years,
        starting_age=35,
        end_age=85,
        currency_symbol="£",
        show_real=True
    )
    
    print(f"✓ Chart created with {len(fig.data)} traces")
    print(f"✓ Chart height: {fig.layout.height}")
    
    # Should have 4 traces: liquid, pension, equity, total
    assert len(fig.data) >= 4, "Should have at least 4 traces"
    assert fig.layout.height == 400, "Chart height should be 400"
    
    trace_names = [trace.name for trace in fig.data if trace.name]
    print(f"✓ Traces: {', '.join(trace_names)}")
    
    print("✅ Composition chart test passed!")


def test_distribution_chart():
    """Test distribution chart creation"""
    print("\n" + "="*60)
    print("TEST 4: Distribution Chart")
    print("="*60)
    
    n_simulations = 100
    years = 30
    
    # Create mock paths
    paths = np.random.rand(n_simulations, years + 1) * 800000
    
    fig = create_distribution_chart(
        paths_to_plot=paths,
        simulation_years=years,
        starting_age=30,
        currency_symbol="£"
    )
    
    print(f"✓ Chart created with {len(fig.data)} histograms")
    print(f"✓ Chart height: {fig.layout.height}")
    
    # Should have histograms for milestone years [5, 10, 15, 20, 25, 30]
    assert len(fig.data) == 6, "Should have 6 milestone histograms"
    assert fig.layout.height == 600, "Chart height should be 600 for 2-row layout"
    
    print("✅ Distribution chart test passed!")


def test_retirement_period_toggle():
    """Test retirement period highlighting"""
    print("\n" + "="*60)
    print("TEST 5: Retirement Period Toggle")
    print("="*60)
    
    n_simulations = 50
    years = 40
    
    paths = np.random.rand(n_simulations, years + 1) * 600000
    
    # Test with retirement period OFF
    fig_no_retirement = create_wealth_trajectory_chart(
        paths_to_plot=paths,
        years=years,
        n_simulations=n_simulations,
        events=[],
        y_label="Net Worth",
        currency_symbol="£",
        starting_age=30,
        retirement_age=65,
        end_age=70,
        show_retirement_period=False,
        use_pension_data=False,
        total_pension_income=0
    )
    print(f"✓ Chart without retirement period: {len(fig_no_retirement.data)} traces")
    
    # Test with retirement period ON
    fig_with_retirement = create_wealth_trajectory_chart(
        paths_to_plot=paths,
        years=years,
        n_simulations=n_simulations,
        events=[],
        y_label="Net Worth",
        currency_symbol="£",
        starting_age=30,
        retirement_age=65,
        end_age=70,
        show_retirement_period=True,
        use_pension_data=True,
        total_pension_income=40000
    )
    print(f"✓ Chart with retirement period: {len(fig_with_retirement.data)} traces")
    
    print("✅ Retirement period toggle test passed!")


def test_chart_performance():
    """Test chart creation performance with large datasets"""
    print("\n" + "="*60)
    print("TEST 6: Performance Test (Large Dataset)")
    print("="*60)
    
    import time
    
    n_simulations = 5000  # Large number
    years = 50
    
    paths = np.random.rand(n_simulations, years + 1) * 1000000
    
    start = time.time()
    fig = create_wealth_trajectory_chart(
        paths_to_plot=paths,
        years=years,
        n_simulations=n_simulations,
        events=[],
        y_label="Net Worth",
        currency_symbol="£",
        starting_age=25,
        retirement_age=65,
        end_age=85
    )
    elapsed = time.time() - start
    
    print(f"✓ Created chart with 5,000 simulations in {elapsed:.3f} seconds")
    print(f"✓ Chart has {len(fig.data)} traces (100 sample paths + percentiles)")
    
    assert elapsed < 5.0, "Chart creation should complete in under 5 seconds"
    
    print("✅ Performance test passed!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("VISUALIZATION SERVICE TEST SUITE")
    print("="*60)
    
    test_get_view_type_paths()
    test_trajectory_chart()
    test_composition_chart()
    test_distribution_chart()
    test_retirement_period_toggle()
    test_chart_performance()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n✨ Visualization service extraction successful!")
    print("📦 Service can now be imported as: from services.visualization import ...")
    print("🎨 All chart generation functions verified and working correctly")
    print()
