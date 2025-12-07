"""
Enhanced Analytics Export
Exports structured data for comprehensive analysis of user financial planning behavior
"""

import sys
import os

# Add project root to path - works both locally and on Render
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
from datetime import datetime
from data_layer.database import SessionLocal, User, Simulation
import json


def export_detailed_analytics():
    """
    Export detailed, structured data for analysis
    Answers questions about:
    - Average age of users
    - Liquid assets and income at given ages
    - Age of property ownership
    - Size of mortgages
    - Expected retirement age
    - Monthly savings amounts
    - Household expenses by age and income
    """
    
    db = SessionLocal()
    try:
        print("\n" + "="*100)
        print("📊 EXPORTING DETAILED ANALYTICS")
        print("="*100)
        
        # Create exports directory
        os.makedirs('exports/analytics', exist_ok=True)
        
        # ========== 1. USER DEMOGRAPHICS ==========
        users = db.query(User).all()
        
        user_data = []
        for user in users:
            user_data.append({
                'user_id': user.id,
                'current_age': user.current_age,
                'target_retirement_age': user.target_retirement_age,
                'years_to_retirement': user.target_retirement_age - user.current_age if user.current_age and user.target_retirement_age else None,
                'country': user.country,
                'account_created': user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
                'last_active': user.last_login.strftime('%Y-%m-%d') if user.last_login else None,
                'account_age_days': (datetime.now() - user.created_at).days if user.created_at else None
            })
        
        users_df = pd.DataFrame(user_data)
        users_df.to_csv('exports/analytics/user_demographics.csv', index=False)
        print(f"✅ Exported user_demographics.csv ({len(users_df)} users)")
        
        
        # ========== 2. SIMULATION DETAILS ==========
        simulations = db.query(Simulation).all()
        
        sim_data = []
        for sim in simulations:
            params = sim.parameters or {}
            
            # Extract key financial metrics from parameters
            initial_liquid = params.get('initial_liquid_wealth', 0)
            initial_property = params.get('initial_property_value', 0)
            initial_mortgage = params.get('initial_mortgage', 0)
            gross_income = params.get('gross_annual_income', 0)
            monthly_expenses = params.get('monthly_expenses', 0)
            starting_age = params.get('starting_age', None)
            retirement_age = params.get('retirement_age', None)
            simulation_years = params.get('simulation_years', None)
            
            # Calculate derived metrics
            annual_expenses = monthly_expenses * 12
            savings_rate = ((gross_income - annual_expenses) / gross_income * 100) if gross_income > 0 else 0
            initial_net_worth = initial_liquid + initial_property - initial_mortgage
            ltv_ratio = (initial_mortgage / initial_property * 100) if initial_property > 0 else 0
            
            sim_data.append({
                'simulation_id': sim.id,
                'user_id': sim.user_id,
                'created_date': sim.created_at.strftime('%Y-%m-%d') if sim.created_at else None,
                'currency': sim.currency,
                
                # Age data
                'starting_age': starting_age,
                'retirement_age': retirement_age,
                'simulation_years': simulation_years,
                
                # Initial wealth position
                'initial_liquid_wealth': initial_liquid,
                'initial_property_value': initial_property,
                'initial_mortgage': initial_mortgage,
                'initial_net_worth': initial_net_worth,
                'initial_liquid_wealth_bracket': sim.initial_liquid_wealth_bracket,
                'initial_property_value_bracket': sim.initial_property_value_bracket,
                
                # Income and expenses
                'gross_annual_income': gross_income,
                'income_bracket': sim.income_bracket,
                'monthly_expenses': monthly_expenses,
                'annual_expenses': annual_expenses,
                'monthly_savings': (gross_income / 12) - monthly_expenses if gross_income > 0 else 0,
                'annual_savings': gross_income - annual_expenses if gross_income > 0 else 0,
                'savings_rate_pct': savings_rate,
                
                # Property metrics
                'ltv_ratio': ltv_ratio,
                'has_property': 1 if initial_property > 0 else 0,
                'has_mortgage': 1 if initial_mortgage > 0 else 0,
                
                # Events
                'number_of_events': sim.number_of_events,
                'has_property_purchase': 1 if sim.has_property_purchase else 0,
                'has_property_sale': 1 if sim.has_property_sale else 0,
                'has_children': 1 if sim.has_children else 0,
                'has_international_move': 1 if sim.has_international_move else 0,
                
                # Outcomes
                'final_net_worth_bracket': sim.final_net_worth_bracket,
                'probability_of_success': sim.probability_of_success
            })
        
        sims_df = pd.DataFrame(sim_data)
        sims_df.to_csv('exports/analytics/simulation_details.csv', index=False)
        print(f"✅ Exported simulation_details.csv ({len(sims_df)} simulations)")
        
        
        # ========== 3. AGE-SEGMENTED ANALYSIS ==========
        # Group data by age ranges for analysis
        if len(sims_df) > 0 and 'starting_age' in sims_df.columns:
            sims_with_age = sims_df[sims_df['starting_age'].notna()].copy()
            
            # Create age groups
            bins = [0, 25, 30, 35, 40, 45, 50, 55, 60, 65, 100]
            labels = ['<25', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65+']
            sims_with_age['age_group'] = pd.cut(sims_with_age['starting_age'], bins=bins, labels=labels, right=False)
            
            age_analysis = sims_with_age.groupby('age_group').agg({
                'simulation_id': 'count',
                'initial_liquid_wealth': ['mean', 'median', 'std'],
                'gross_annual_income': ['mean', 'median', 'std'],
                'monthly_expenses': ['mean', 'median', 'std'],
                'monthly_savings': ['mean', 'median'],
                'savings_rate_pct': ['mean', 'median'],
                'initial_property_value': 'mean',
                'initial_mortgage': 'mean',
                'has_property': 'sum',
                'has_mortgage': 'sum',
                'has_children': 'sum',
                'retirement_age': ['mean', 'median']
            }).round(2)
            
            age_analysis.columns = ['_'.join(col).strip() for col in age_analysis.columns.values]
            age_analysis = age_analysis.reset_index()
            age_analysis.to_csv('exports/analytics/age_segmented_analysis.csv', index=False)
            print(f"✅ Exported age_segmented_analysis.csv")
        
        
        # ========== 4. INCOME-SEGMENTED ANALYSIS ==========
        if len(sims_df) > 0:
            sims_with_income = sims_df[sims_df['gross_annual_income'] > 0].copy()
            
            # Create income groups based on brackets
            income_analysis = sims_with_income.groupby('income_bracket').agg({
                'simulation_id': 'count',
                'starting_age': ['mean', 'median'],
                'initial_liquid_wealth': ['mean', 'median'],
                'monthly_expenses': ['mean', 'median'],
                'monthly_savings': ['mean', 'median'],
                'savings_rate_pct': ['mean', 'median'],
                'has_property': 'sum',
                'has_children': 'sum',
                'retirement_age': ['mean', 'median']
            }).round(2)
            
            income_analysis.columns = ['_'.join(col).strip() for col in income_analysis.columns.values]
            income_analysis = income_analysis.reset_index()
            income_analysis.to_csv('exports/analytics/income_segmented_analysis.csv', index=False)
            print(f"✅ Exported income_segmented_analysis.csv")
        
        
        # ========== 5. PROPERTY OWNERSHIP ANALYSIS ==========
        if len(sims_df) > 0:
            property_owners = sims_df[sims_df['has_property'] == 1].copy()
            
            if len(property_owners) > 0:
                property_analysis = pd.DataFrame([{
                    'total_property_owners': len(property_owners),
                    'avg_age_with_property': property_owners['starting_age'].mean(),
                    'median_age_with_property': property_owners['starting_age'].median(),
                    'avg_property_value': property_owners['initial_property_value'].mean(),
                    'median_property_value': property_owners['initial_property_value'].median(),
                    'avg_mortgage': property_owners[property_owners['has_mortgage'] == 1]['initial_mortgage'].mean(),
                    'median_mortgage': property_owners[property_owners['has_mortgage'] == 1]['initial_mortgage'].median(),
                    'avg_ltv_ratio': property_owners[property_owners['has_mortgage'] == 1]['ltv_ratio'].mean(),
                    'pct_with_mortgage': (property_owners['has_mortgage'].sum() / len(property_owners) * 100)
                }])
                
                property_analysis.to_csv('exports/analytics/property_ownership_summary.csv', index=False)
                print(f"✅ Exported property_ownership_summary.csv")
        
        
        # ========== 6. RETIREMENT PLANNING ANALYSIS ==========
        if len(sims_df) > 0:
            retirement_data = sims_df[sims_df['retirement_age'].notna()].copy()
            
            if len(retirement_data) > 0:
                retirement_analysis = pd.DataFrame([{
                    'total_simulations': len(retirement_data),
                    'avg_current_age': retirement_data['starting_age'].mean(),
                    'avg_target_retirement_age': retirement_data['retirement_age'].mean(),
                    'median_target_retirement_age': retirement_data['retirement_age'].median(),
                    'avg_years_to_retirement': retirement_data['simulation_years'].mean(),
                    'median_years_to_retirement': retirement_data['simulation_years'].median(),
                    'pct_early_retirement_55': (retirement_data['retirement_age'] <= 55).sum() / len(retirement_data) * 100,
                    'pct_early_retirement_60': (retirement_data['retirement_age'] <= 60).sum() / len(retirement_data) * 100,
                    'pct_standard_retirement_65': (retirement_data['retirement_age'] == 65).sum() / len(retirement_data) * 100,
                    'pct_late_retirement_70plus': (retirement_data['retirement_age'] >= 70).sum() / len(retirement_data) * 100
                }])
                
                retirement_analysis.to_csv('exports/analytics/retirement_planning_summary.csv', index=False)
                print(f"✅ Exported retirement_planning_summary.csv")
        
        
        # ========== 7. SAVINGS BEHAVIOR ANALYSIS ==========
        if len(sims_df) > 0:
            savings_data = sims_df[sims_df['monthly_savings'].notna()].copy()
            
            # Create savings rate categories
            savings_data['savings_category'] = pd.cut(
                savings_data['savings_rate_pct'],
                bins=[-100, 0, 10, 20, 30, 100],
                labels=['Deficit', '0-10%', '10-20%', '20-30%', '30%+']
            )
            
            savings_analysis = savings_data.groupby('savings_category').agg({
                'simulation_id': 'count',
                'starting_age': ['mean', 'median'],
                'gross_annual_income': ['mean', 'median'],
                'monthly_expenses': ['mean', 'median'],
                'monthly_savings': ['mean', 'median'],
                'initial_liquid_wealth': ['mean', 'median']
            }).round(2)
            
            savings_analysis.columns = ['_'.join(col).strip() for col in savings_analysis.columns.values]
            savings_analysis = savings_analysis.reset_index()
            savings_analysis.to_csv('exports/analytics/savings_behavior_analysis.csv', index=False)
            print(f"✅ Exported savings_behavior_analysis.csv")
        
        
        # ========== 8. SUMMARY STATISTICS ==========
        summary_stats = pd.DataFrame([{
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_users': len(users_df),
            'total_simulations': len(sims_df),
            'simulations_per_user': len(sims_df) / len(users_df) if len(users_df) > 0 else 0,
            'avg_user_age': users_df['current_age'].mean() if 'current_age' in users_df.columns else None,
            'avg_retirement_age': users_df['target_retirement_age'].mean() if 'target_retirement_age' in users_df.columns else None,
            'avg_initial_liquid_wealth': sims_df['initial_liquid_wealth'].mean() if 'initial_liquid_wealth' in sims_df.columns else None,
            'avg_annual_income': sims_df['gross_annual_income'].mean() if 'gross_annual_income' in sims_df.columns else None,
            'avg_monthly_expenses': sims_df['monthly_expenses'].mean() if 'monthly_expenses' in sims_df.columns else None,
            'avg_monthly_savings': sims_df['monthly_savings'].mean() if 'monthly_savings' in sims_df.columns else None,
            'pct_with_property': (sims_df['has_property'].sum() / len(sims_df) * 100) if len(sims_df) > 0 else 0,
            'pct_with_children_event': (sims_df['has_children'].sum() / len(sims_df) * 100) if len(sims_df) > 0 else 0
        }])
        
        summary_stats.to_csv('exports/analytics/summary_statistics.csv', index=False)
        print(f"✅ Exported summary_statistics.csv")
        
        
        print("\n" + "="*100)
        print("✅ EXPORT COMPLETE")
        print("="*100)
        print("\nExported files to 'exports/analytics/' directory:")
        print("  1. user_demographics.csv - User age, retirement plans, account info")
        print("  2. simulation_details.csv - All simulation parameters and metrics")
        print("  3. age_segmented_analysis.csv - Financial metrics grouped by age")
        print("  4. income_segmented_analysis.csv - Behavior patterns by income level")
        print("  5. property_ownership_summary.csv - Property and mortgage statistics")
        print("  6. retirement_planning_summary.csv - Retirement age distributions")
        print("  7. savings_behavior_analysis.csv - Savings rates and patterns")
        print("  8. summary_statistics.csv - Overall platform statistics")
        print("\n" + "="*100)
        
    finally:
        db.close()


if __name__ == "__main__":
    export_detailed_analytics()
