"""
Data tracking module for FinSim
Saves simulation data to database for analysis
"""

from datetime import datetime
from database import SessionLocal, Simulation, get_wealth_bracket, get_income_bracket, get_age_range


def save_simulation(user_id: int, simulation_params: dict, results: dict = None):
    """
    Save simulation run to database with anonymized data
    
    Args:
        user_id: User ID
        simulation_params: Dictionary of all simulation parameters
        results: Optional results dictionary
    """
    db = SessionLocal()
    try:
        # Extract key parameters
        currency = simulation_params.get('currency', 'USD')
        initial_liquid = simulation_params.get('initial_liquid_wealth', 0)
        initial_property = simulation_params.get('initial_property_value', 0)
        income = simulation_params.get('gross_annual_income', 0)
        events = simulation_params.get('events', [])
        
        # Anonymize data into brackets
        wealth_bracket = get_wealth_bracket(initial_liquid)
        property_bracket = get_wealth_bracket(initial_property)
        income_bracket = get_income_bracket(income)
        
        # Analyze events
        has_property_purchase = any(e.get('type') == 'property_purchase' for e in events)
        has_property_sale = any(e.get('type') == 'property_sale' for e in events)
        has_children = any(e.get('type') == 'expense_change' and 'child' in e.get('name', '').lower() for e in events)
        has_international_move = any('move' in e.get('name', '').lower() or 'dublin' in e.get('name', '').lower() or 'international' in e.get('name', '').lower() for e in events)
        
        # Calculate final net worth bracket if results provided
        final_net_worth_bracket = None
        probability_of_success = None
        
        if results:
            final_net_worth = results.get('net_worth', [[0]])[:, -1].mean()
            final_net_worth_bracket = get_wealth_bracket(final_net_worth)
            
            # Calculate probability of growth
            initial_net_worth = results.get('net_worth', [[0]])[:, 0]
            final_values = results.get('net_worth', [[0]])[:, -1]
            if len(initial_net_worth) > 0 and len(final_values) > 0:
                probability_of_success = (final_values > initial_net_worth[0]).mean()
        
        # Create simulation record
        simulation = Simulation(
            user_id=user_id,
            name=simulation_params.get('name', f"Simulation {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
            currency=currency,
            initial_liquid_wealth_bracket=wealth_bracket,
            initial_property_value_bracket=property_bracket,
            income_bracket=income_bracket,
            parameters=simulation_params,  # Store full params for user's reference
            has_property_purchase=has_property_purchase,
            has_property_sale=has_property_sale,
            has_international_move=has_international_move,
            has_children=has_children,
            number_of_events=len(events),
            final_net_worth_bracket=final_net_worth_bracket,
            probability_of_success=probability_of_success,
            created_at=datetime.now()
        )
        
        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        
        return True, simulation.id
        
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def get_user_simulations(user_id: int, limit: int = 10):
    """Get user's recent simulations"""
    db = SessionLocal()
    try:
        simulations = db.query(Simulation).filter(
            Simulation.user_id == user_id
        ).order_by(Simulation.created_at.desc()).limit(limit).all()
        
        return simulations
        
    finally:
        db.close()


def get_simulation_by_id(simulation_id: int, user_id: int):
    """Get specific simulation (ensure it belongs to user)"""
    db = SessionLocal()
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        ).first()
        
        return simulation
        
    finally:
        db.close()


def delete_simulation(simulation_id: int, user_id: int):
    """Delete a simulation (ensure it belongs to user)"""
    db = SessionLocal()
    try:
        simulation = db.query(Simulation).filter(
            Simulation.id == simulation_id,
            Simulation.user_id == user_id
        ).first()
        
        if simulation:
            db.delete(simulation)
            db.commit()
            return True, "Simulation deleted"
        else:
            return False, "Simulation not found"
            
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def get_aggregated_insights(period: str = None):
    """
    Get aggregated anonymous insights from all simulations
    Used for research and trend analysis
    
    Args:
        period: Optional period filter (e.g., "2024-Q1")
    """
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        # Base query
        query = db.query(
            func.count(Simulation.id).label('total_simulations'),
            func.avg(Simulation.number_of_events).label('avg_events'),
            func.sum(Simulation.has_property_purchase.cast(db.Integer)).label('property_purchases'),
            func.sum(Simulation.has_children.cast(db.Integer)).label('has_children_count'),
            func.sum(Simulation.has_international_move.cast(db.Integer)).label('international_moves')
        )
        
        # Apply period filter if provided
        if period:
            # Filter by creation date matching period
            # Period format: "2024-Q1" or "2024-11"
            pass  # Implement date filtering as needed
        
        result = query.first()
        
        return {
            'total_simulations': result.total_simulations or 0,
            'avg_events_per_simulation': round(result.avg_events, 2) if result.avg_events else 0,
            'property_purchase_percentage': round((result.property_purchases / result.total_simulations * 100), 1) if result.total_simulations > 0 else 0,
            'planning_for_children_percentage': round((result.has_children_count / result.total_simulations * 100), 1) if result.total_simulations > 0 else 0,
            'international_moves_percentage': round((result.international_moves / result.total_simulations * 100), 1) if result.total_simulations > 0 else 0,
        }
        
    finally:
        db.close()


def get_wealth_distribution():
    """Get distribution of users across wealth brackets (anonymized)"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        # Count simulations by wealth bracket
        results = db.query(
            Simulation.initial_liquid_wealth_bracket,
            func.count(Simulation.id).label('count')
        ).group_by(Simulation.initial_liquid_wealth_bracket).all()
        
        distribution = {result[0]: result[1] for result in results if result[0]}
        
        return distribution
        
    finally:
        db.close()


def get_income_distribution():
    """Get distribution of users across income brackets (anonymized)"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        
        results = db.query(
            Simulation.income_bracket,
            func.count(Simulation.id).label('count')
        ).group_by(Simulation.income_bracket).all()
        
        distribution = {result[0]: result[1] for result in results if result[0]}
        
        return distribution
        
    finally:
        db.close()