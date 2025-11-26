"""
Unit Tests for Currency Manager
================================
Tests for the canonical base currency system
"""

import pytest
import streamlit as st
from currency_manager import (
    BASE_CURRENCY,
    to_base_currency,
    from_base_currency,
    convert_events_to_base,
    convert_events_from_base,
    convert_simulation_results_to_display,
)
import numpy as np


class TestBasicConversions:
    """Test basic currency conversion functions"""
    
    def test_base_currency_to_itself(self):
        """Converting EUR to EUR should return same value"""
        amount = 100000.0
        result = to_base_currency(amount, 'EUR')
        assert result == amount
        
        result2 = from_base_currency(amount, 'EUR')
        assert result2 == amount
    
    def test_roundtrip_conversion(self):
        """Converting to base and back should preserve value (within tolerance)"""
        original_amount = 100000.0
        original_currency = 'USD'
        
        # USD → EUR → USD
        base_amount = to_base_currency(original_amount, original_currency)
        back_to_original = from_base_currency(base_amount, original_currency)
        
        # Should be very close (allowing for small floating point errors)
        assert abs(back_to_original - original_amount) < 0.01
    
    def test_conversion_with_multiple_currencies(self):
        """Test conversion through multiple currencies"""
        amount = 50000.0
        
        # Start in GBP
        base_from_gbp = to_base_currency(amount, 'GBP')
        
        # Convert base to USD
        usd_amount = from_base_currency(base_from_gbp, 'USD')
        
        # Convert USD back to base
        base_from_usd = to_base_currency(usd_amount, 'USD')
        
        # Should get back to original base amount
        assert abs(base_from_gbp - base_from_usd) < 0.01
    
    def test_zero_amount(self):
        """Zero should convert to zero"""
        assert to_base_currency(0, 'USD') == 0
        assert from_base_currency(0, 'GBP') == 0
    
    def test_negative_amount(self):
        """Negative amounts should convert correctly"""
        amount = -50000.0
        base = to_base_currency(amount, 'USD')
        assert base < 0
        
        back = from_base_currency(base, 'USD')
        assert abs(back - amount) < 0.01


class TestEventConversions:
    """Test event conversion functions"""
    
    def test_property_purchase_conversion(self):
        """Test property purchase event conversion"""
        event = {
            'type': 'property_purchase',
            'year': 5,
            'name': 'Buy House',
            'property_price': 500000,
            'down_payment': 100000,
            'mortgage_amount': 400000,
            'new_mortgage_payment': 2000
        }
        
        # Convert to base
        base_events = convert_events_to_base([event], 'USD')
        base_event = base_events[0]
        
        # Values should be different (converted to EUR)
        assert base_event['property_price'] != event['property_price']
        
        # Convert back
        export_events = convert_events_from_base(base_events, 'USD')
        export_event = export_events[0]
        
        # Should be close to original
        assert abs(export_event['property_price'] - event['property_price']) < 1.0
    
    def test_one_time_expense_conversion(self):
        """Test one-time expense conversion"""
        event = {
            'type': 'one_time_expense',
            'year': 3,
            'name': 'Wedding',
            'amount': 30000
        }
        
        base_events = convert_events_to_base([event], 'GBP')
        assert base_events[0]['amount'] != event['amount']
        
        export_events = convert_events_from_base(base_events, 'GBP')
        assert abs(export_events[0]['amount'] - event['amount']) < 1.0
    
    def test_expense_change_conversion(self):
        """Test expense change conversion"""
        event = {
            'type': 'expense_change',
            'year': 2,
            'name': 'Increase spending',
            'monthly_change': 500
        }
        
        base_events = convert_events_to_base([event], 'USD')
        export_events = convert_events_from_base(base_events, 'USD')
        
        assert abs(export_events[0]['monthly_change'] - event['monthly_change']) < 1.0
    
    def test_multiple_events_conversion(self):
        """Test converting multiple events at once"""
        events = [
            {
                'type': 'windfall',
                'year': 1,
                'name': 'Bonus',
                'amount': 10000
            },
            {
                'type': 'rental_income',
                'year': 5,
                'name': 'Rental',
                'monthly_rental': 1500
            },
            {
                'type': 'property_sale',
                'year': 10,
                'name': 'Sell house',
                'sale_price': 600000,
                'mortgage_payoff': 300000,
                'selling_costs': 30000
            }
        ]
        
        base_events = convert_events_to_base(events, 'CAD')
        assert len(base_events) == 3
        
        export_events = convert_events_from_base(base_events, 'CAD')
        assert len(export_events) == 3
        
        # Check amounts are close to original
        assert abs(export_events[0]['amount'] - events[0]['amount']) < 1.0
        assert abs(export_events[2]['sale_price'] - events[2]['sale_price']) < 1.0


class TestSimulationResultsConversion:
    """Test simulation results conversion"""
    
    def test_results_conversion_to_base_currency(self):
        """Converting to base currency should return unchanged"""
        results = {
            'net_worth': np.array([[100000, 110000, 120000]]),
            'liquid_wealth': np.array([[50000, 55000, 60000]]),
            'pension_wealth': np.array([[30000, 35000, 40000]]),
            'property_value': np.array([[200000, 210000, 220000]]),
            'mortgage_balance': np.array([[100000, 90000, 80000]]),
            'inflation_rates': np.array([[0.02, 0.025, 0.03]])
        }
        
        converted = convert_simulation_results_to_display(results, BASE_CURRENCY)
        
        # Should be identical for base currency
        assert np.array_equal(converted['net_worth'], results['net_worth'])
        assert np.array_equal(converted['inflation_rates'], results['inflation_rates'])
    
    def test_results_conversion_preserves_shape(self):
        """Conversion should preserve array shapes"""
        results = {
            'net_worth': np.random.rand(1000, 31),  # 1000 simulations, 31 years
            'liquid_wealth': np.random.rand(1000, 31),
            'pension_wealth': np.random.rand(1000, 31),
            'property_value': np.random.rand(1000, 31),
            'mortgage_balance': np.random.rand(1000, 31),
            'inflation_rates': np.random.rand(1000, 30)
        }
        
        converted = convert_simulation_results_to_display(results, 'USD')
        
        assert converted['net_worth'].shape == results['net_worth'].shape
        assert converted['inflation_rates'].shape == results['inflation_rates'].shape
    
    def test_results_conversion_scales_correctly(self):
        """Converted amounts should scale by exchange rate"""
        results = {
            'net_worth': np.array([[100000.0]]),
            'liquid_wealth': np.array([[100000.0]]),
            'pension_wealth': np.array([[0.0]]),
            'property_value': np.array([[0.0]]),
            'mortgage_balance': np.array([[0.0]]),
            'inflation_rates': np.array([[0.02]])
        }
        
        # Convert EUR to USD (should be roughly 1.07x)
        converted = convert_simulation_results_to_display(results, 'USD')
        
        # USD amount should be larger than EUR amount
        assert converted['net_worth'][0, 0] > results['net_worth'][0, 0]
        
        # Inflation rates should be unchanged
        assert converted['inflation_rates'][0, 0] == results['inflation_rates'][0, 0]


class TestNoCumulativeDrift:
    """Test that repeated conversions don't cause drift"""
    
    def test_repeated_display_conversions_no_drift(self):
        """Multiple display conversions from same base shouldn't drift"""
        base_amount = 100000.0
        
        # Convert to USD many times
        conversions = []
        for _ in range(100):
            usd_amount = from_base_currency(base_amount, 'USD')
            conversions.append(usd_amount)
        
        # All should be identical (no drift)
        assert all(abs(c - conversions[0]) < 0.01 for c in conversions)
    
    def test_base_storage_prevents_drift(self):
        """Storing in base prevents drift from currency switches"""
        original_amount = 50000.0
        
        # Simulate multiple currency switches
        currencies = ['USD', 'GBP', 'EUR', 'CAD', 'USD', 'EUR', 'GBP', 'USD']
        
        # Store in base once
        base_amount = to_base_currency(original_amount, 'USD')
        
        # Convert to each currency
        displayed_amounts = []
        for currency in currencies:
            displayed = from_base_currency(base_amount, currency)
            displayed_amounts.append(displayed)
        
        # Convert all back to USD
        back_to_usd = [
            from_base_currency(to_base_currency(amt, curr), 'USD')
            for amt, curr in zip(displayed_amounts, currencies)
        ]
        
        # All should be very close to original
        for amount in back_to_usd:
            assert abs(amount - original_amount) < 1.0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_very_large_amounts(self):
        """Test with very large monetary amounts"""
        large_amount = 1_000_000_000.0  # 1 billion
        
        base = to_base_currency(large_amount, 'USD')
        back = from_base_currency(base, 'USD')
        
        # Should handle large numbers
        assert abs(back - large_amount) / large_amount < 0.0001  # Within 0.01%
    
    def test_very_small_amounts(self):
        """Test with very small monetary amounts"""
        small_amount = 0.01
        
        base = to_base_currency(small_amount, 'USD')
        back = from_base_currency(base, 'USD')
        
        # Should handle small numbers
        assert abs(back - small_amount) < 0.01
    
    def test_fractional_amounts(self):
        """Test with fractional currency amounts"""
        amount = 12345.67
        
        base = to_base_currency(amount, 'GBP')
        back = from_base_currency(base, 'GBP')
        
        assert abs(back - amount) < 0.01


# Integration test example
class TestIntegrationScenario:
    """Test a realistic user workflow"""
    
    def test_complete_user_flow(self):
        """Test complete flow: input → store → simulate → display → export"""
        
        # 1. User enters amount in USD
        user_input_usd = 100000.0
        
        # 2. Store in base (EUR)
        base_liquid_wealth = to_base_currency(user_input_usd, 'USD')
        
        # 3. User switches to GBP
        displayed_in_gbp = from_base_currency(base_liquid_wealth, 'GBP')
        
        # 4. User runs simulation (uses base amount)
        # Simulate simple wealth projection
        simulation_results = {
            'net_worth': np.array([[base_liquid_wealth * 1.5]]),
            'liquid_wealth': np.array([[base_liquid_wealth * 1.5]]),
            'pension_wealth': np.array([[0.0]]),
            'property_value': np.array([[0.0]]),
            'mortgage_balance': np.array([[0.0]]),
            'inflation_rates': np.array([[0.02]])
        }
        
        # 5. Display results in GBP
        display_results = convert_simulation_results_to_display(
            simulation_results, 
            'GBP'
        )
        
        # 6. Export in USD
        export_results = convert_simulation_results_to_display(
            simulation_results,
            'USD'
        )
        
        # Verify consistency
        # Original input and export should be close (both in USD)
        export_final = export_results['net_worth'][0, 0]
        expected_final = user_input_usd * 1.5
        
        assert abs(export_final - expected_final) / expected_final < 0.01


# Test fixtures and helpers
@pytest.fixture
def sample_events():
    """Fixture providing sample events for testing"""
    return [
        {
            'type': 'property_purchase',
            'year': 5,
            'name': 'Buy House',
            'property_price': 500000,
            'down_payment': 100000,
            'mortgage_amount': 400000,
            'new_mortgage_payment': 2000
        },
        {
            'type': 'windfall',
            'year': 3,
            'name': 'Inheritance',
            'amount': 50000
        }
    ]


@pytest.fixture
def sample_results():
    """Fixture providing sample simulation results"""
    return {
        'net_worth': np.random.rand(1000, 31) * 500000,
        'liquid_wealth': np.random.rand(1000, 31) * 200000,
        'pension_wealth': np.random.rand(1000, 31) * 150000,
        'property_value': np.random.rand(1000, 31) * 400000,
        'mortgage_balance': np.random.rand(1000, 31) * 250000,
        'inflation_rates': np.random.rand(1000, 30) * 0.05
    }


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])