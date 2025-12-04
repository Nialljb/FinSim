"""
Pension Planning UI for FinSim
Interactive pension calculator and planner for UK pensions
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from pension_planner import (
    # State Pension
    calculate_state_pension_age,
    estimate_ni_qualifying_years,
    calculate_state_pension_amount,
    forecast_state_pension,
    STATE_PENSION_FULL_AMOUNT,
    QUALIFYING_YEARS_FULL,
    QUALIFYING_YEARS_MIN,
    
    # USS
    calculate_uss_contributions,
    project_uss_pension,
    calculate_current_uss_pension_value,
    project_avc_growth,
    USS_RETIREMENT_AGE,
    USS_ACCRUAL_RATE,
    USS_LUMP_SUM_MULTIPLE,
    
    # SIPP
    calculate_sipp_tax_relief,
    project_sipp_growth,
    SIPP_ANNUAL_ALLOWANCE,
    SIPP_LUMP_SUM_TAX_FREE,
    
    # Combined
    calculate_total_retirement_income,
    calculate_pension_drawdown,
    safe_withdrawal_rate,
    
    # Visualization
    create_pension_projection_chart,
    create_pension_pie_chart
)

from database import SessionLocal, PensionPlan
from currency_manager import format_currency


def show_pension_planner_tab(user_id):
    """Main pension planner interface"""
    
    st.title("🎯 UK Pension Planner")
    
    st.markdown("""
    Plan your retirement with confidence. Track your State Pension, workplace pensions (USS), 
    and private pensions (SIPP) all in one place.
    """)
    
    # Create tabs for different pension types
    pension_tabs = st.tabs([
        "📊 Overview",
        "🏛️ State Pension",
        "🎓 USS Pension",
        "💰 SIPP",
        "📈 Retirement Income"
    ])
    
    # Initialize session state for pension data
    if 'pension_data' not in st.session_state:
        st.session_state.pension_data = load_pension_plan(user_id)
    
    pension_data = st.session_state.pension_data
    
    # ========================================================================
    # TAB 1: OVERVIEW
    # ========================================================================
    with pension_tabs[0]:
        show_pension_overview(pension_data, user_id)
    
    # ========================================================================
    # TAB 2: STATE PENSION
    # ========================================================================
    with pension_tabs[1]:
        show_state_pension_calculator(pension_data, user_id)
    
    # ========================================================================
    # TAB 3: USS PENSION
    # ========================================================================
    with pension_tabs[2]:
        show_uss_pension_calculator(pension_data, user_id)
    
    # ========================================================================
    # TAB 4: SIPP
    # ========================================================================
    with pension_tabs[3]:
        show_sipp_calculator(pension_data, user_id)
    
    # ========================================================================
    # TAB 5: RETIREMENT INCOME
    # ========================================================================
    with pension_tabs[4]:
        show_retirement_income_planner(pension_data, user_id)


def show_pension_overview(pension_data, user_id):
    """Overview dashboard showing all pension sources"""
    
    st.subheader("Your Pension Overview")
    
    # Calculate totals
    state_pension = pension_data.get('state_pension_annual_amount', 0)
    uss_pension = pension_data.get('uss_projected_annual_pension', 0)
    sipp_value = pension_data.get('sipp_projected_value', 0)
    
    # USS AVC projection
    uss_avc_value = pension_data.get('uss_avc_projected_value', 0)
    uss_avc_annual_income = uss_avc_value * 0.04 if uss_avc_value > 0 else 0
    
    # Estimate SIPP annual drawdown (4% rule)
    sipp_annual_income = sipp_value * 0.04 if sipp_value > 0 else 0
    
    total_income = state_pension + uss_pension + uss_avc_annual_income + sipp_annual_income
    
    # Display key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "State Pension",
            f"£{state_pension:,.0f}/year",
            f"£{state_pension/12:,.0f}/month"
        )
    
    with col2:
        st.metric(
            "USS Pension",
            f"£{uss_pension:,.0f}/year",
            f"£{uss_pension/12:,.0f}/month" if uss_pension > 0 else "Not enrolled"
        )
    
    with col3:
        st.metric(
            "USS AVC",
            f"£{uss_avc_annual_income:,.0f}/year",
            f"£{uss_avc_value:,.0f} pot" if uss_avc_value > 0 else "Not enabled"
        )
    
    with col4:
        st.metric(
            "SIPP",
            f"£{sipp_annual_income:,.0f}/year",
            f"£{sipp_value:,.0f} pot"
        )
    
    with col5:
        st.metric(
            "Total Income",
            f"£{total_income:,.0f}",
            f"£{total_income/12:,.0f}/month"
        )
    
    # Visual breakdown
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if total_income > 0:
            fig = create_pension_pie_chart(state_pension, uss_pension, sipp_annual_income, uss_avc_annual_income)
            st.plotly_chart(fig, use_container_width=True, key="pension_overview_pie_chart")
        else:
            st.info("📝 Complete the pension sections below to see your retirement income breakdown")
    
    with col2:
        st.markdown("### Retirement Readiness")
        
        desired_income = pension_data.get('desired_retirement_income', 0)
        
        if desired_income > 0:
            coverage = (total_income / desired_income) * 100
            
            st.progress(min(coverage / 100, 1.0))
            st.markdown(f"**{coverage:.0f}%** of desired income covered")
            
            if coverage >= 100:
                st.success("✅ You're on track to meet your retirement income goal!")
            elif coverage >= 75:
                st.warning(f"⚠️ You're close! Need £{desired_income - total_income:,.0f} more per year")
            else:
                st.error(f"❌ Shortfall: £{desired_income - total_income:,.0f} per year")
        else:
            desired = st.number_input(
                "What annual retirement income do you want?",
                min_value=0,
                value=30000,
                step=1000,
                help="Your target annual income in retirement"
            )
            if st.button("Set Goal"):
                pension_data['desired_retirement_income'] = desired
                save_pension_plan(pension_data, user_id)
                st.rerun()
        
        # Simulation end age
        st.markdown("---")
        st.markdown("**Simulation Settings**")
        retirement_age = pension_data.get('target_retirement_age', 67)
        current_end_age = pension_data.get('simulation_end_age', 0)
        # Ensure end_age is at least retirement_age
        default_end_age = max(current_end_age, retirement_age + 20) if current_end_age > 0 else min(retirement_age + 20, 90)
        
        end_age = st.number_input(
            "Simulate Until Age",
            min_value=retirement_age,
            max_value=100,
            value=default_end_age,
            step=1,
            help="Age to end retirement simulation (for use in main simulator)"
        )
        if st.button("Update Simulation Age"):
            pension_data['simulation_end_age'] = end_age
            save_pension_plan(pension_data, user_id)
            st.success(f"✅ Will simulate until age {end_age}")
    
    # Quick actions
    st.markdown("---")
    st.markdown("### Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not pension_data.get('state_pension_enabled', False):
            st.info("🏛️ Go to **State Pension** tab to set up your State Pension forecast")
    
    with col2:
        if not pension_data.get('uss_enabled', False):
            st.info("🎓 Go to **USS Pension** tab to set up your USS pension")
    
    with col3:
        if not pension_data.get('sipp_enabled', False):
            st.info("💰 Go to **SIPP** tab to set up your personal pension")


def show_state_pension_calculator(pension_data, user_id):
    """State Pension calculator and tracker"""
    
    st.subheader("🏛️ UK State Pension Calculator")
    
    st.info("""
    The UK State Pension is a regular payment from the government you can claim when you reach State Pension age.
    You need at least 10 qualifying years of National Insurance contributions to get any State Pension,
    and 35 years to get the full amount (£{:,.2f}/year in 2025/26).
    """.format(STATE_PENSION_FULL_AMOUNT))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Date of birth
        current_dob = pension_data.get('date_of_birth')
        if current_dob:
            dob = datetime.strptime(current_dob, '%Y-%m-%d').date()
        else:
            dob = date(1980, 1, 1)
        
        date_of_birth = st.date_input(
            "Date of Birth",
            value=dob,
            min_value=date(1940, 1, 1),
            max_value=date.today(),
            help="Your date of birth determines your State Pension age"
        )
        
        # Calculate State Pension age
        pension_age = calculate_state_pension_age(date_of_birth)
        current_age = (date.today() - date_of_birth).days // 365
        years_to_pension = max(0, pension_age - current_age)
        
        st.info(f"📅 Your State Pension age is **{pension_age}** (in {years_to_pension} years)")
        
        # NI years
        col_a, col_b = st.columns(2)
        
        with col_a:
            ni_years = st.number_input(
                "Current NI qualifying years",
                min_value=0,
                max_value=50,
                value=pension_data.get('state_pension_ni_years', 0),
                help="Check your NI record at gov.uk/check-national-insurance-record"
            )
        
        with col_b:
            employment_status = st.selectbox(
                "Employment Status",
                ["Employed", "Self-Employed", "Unemployed (claiming credits)", "Not working"],
                help="This affects future NI contributions"
            )
        
        # Project future years
        if employment_status in ["Employed", "Self-Employed"]:
            projected_future_years = years_to_pension
        elif employment_status == "Unemployed (claiming credits)":
            projected_future_years = int(years_to_pension * 0.8)  # May get some credits
        else:
            projected_future_years = st.number_input(
                "Expected future qualifying years",
                min_value=0,
                max_value=years_to_pension,
                value=0,
                help="Years you expect to contribute NI in the future"
            )
        
        # Calculate forecast
        forecast = forecast_state_pension(date_of_birth, ni_years, projected_future_years)
        
    with col2:
        st.markdown("### Your State Pension")
        
        # Show current vs projected in tabs if they have NI years
        if ni_years > 0:
            tab_current, tab_projected = st.tabs(["📊 Current Position", "🎯 At Retirement"])
            
            with tab_current:
                st.markdown("**Based on Current NI Years**")
                # Calculate current entitlement
                current_amount = calculate_state_pension_amount(ni_years)
                current_monthly = current_amount / 12
                
                st.metric(
                    "NI Years Accrued",
                    f"{ni_years} years",
                    help="Qualifying years already on your NI record"
                )
                st.metric(
                    "Current Annual Entitlement",
                    f"£{current_amount:,.2f}",
                    help="What you'd get now if you reached pension age"
                )
                st.metric(
                    "Current Monthly Amount",
                    f"£{current_monthly:,.2f}"
                )
                
                # Progress bar for current
                current_progress = min(ni_years / QUALIFYING_YEARS_FULL, 1.0)
                st.progress(current_progress)
                st.caption(f"{current_progress*100:.0f}% of full pension achieved")
            
            with tab_projected:
                st.markdown(f"**At Age {pension_age}**")
                st.metric(
                    "Projected Total Years",
                    f"{forecast['qualifying_years']} years",
                    delta=f"+{projected_future_years} years"
                )
                st.metric(
                    "Projected Annual Pension",
                    f"£{forecast['annual_amount']:,.2f}",
                    delta=f"+£{forecast['annual_amount'] - current_amount:,.0f}"
                )
                st.metric(
                    "Projected Monthly Pension",
                    f"£{forecast['monthly_amount']:,.2f}"
                )
                
                # Progress to full pension
                progress = min(forecast['qualifying_years'] / QUALIFYING_YEARS_FULL, 1.0)
                st.progress(progress)
                
                if forecast['is_full_pension']:
                    st.success("✅ Full State Pension")
                elif forecast['qualifying_years'] >= QUALIFYING_YEARS_MIN:
                    missing_years = QUALIFYING_YEARS_FULL - forecast['qualifying_years']
                    st.warning(f"⚠️ {missing_years} more years for full pension")
                else:
                    st.error(f"❌ Need {QUALIFYING_YEARS_MIN - forecast['qualifying_years']} more years to qualify")
        else:
            # No NI years yet, just show projection
            st.metric("Total Qualifying Years", f"{forecast['qualifying_years']}")
            st.metric("Annual Pension", f"£{forecast['annual_amount']:,.2f}")
            st.metric("Monthly Pension", f"£{forecast['monthly_amount']:,.2f}")
            
            # Progress to full pension
            progress = min(forecast['qualifying_years'] / QUALIFYING_YEARS_FULL, 1.0)
            st.progress(progress)
            
            if forecast['is_full_pension']:
                st.success("✅ Full State Pension")
            elif forecast['qualifying_years'] >= QUALIFYING_YEARS_MIN:
                missing_years = QUALIFYING_YEARS_FULL - forecast['qualifying_years']
                st.warning(f"⚠️ {missing_years} more years for full pension")
            else:
                st.error(f"❌ Need {QUALIFYING_YEARS_MIN - forecast['qualifying_years']} more years to qualify")
    
    # Gaps and options
    st.markdown("---")
    st.markdown("### 💡 Improve Your State Pension")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Check for gaps in your NI record:**
        - Visit [Check your National Insurance record](https://www.gov.uk/check-national-insurance-record)
        - You may be able to buy missing years (usually £800-900/year)
        - You have up to 6 years to fill gaps
        """)
    
    with col2:
        st.markdown("""
        **Ways to build qualifying years:**
        - Working and paying NI contributions
        - Claiming certain benefits (Universal Credit, etc.)
        - Getting NI credits as a parent or carer
        - Voluntary NI contributions
        """)
    
    # Save button
    if st.button("💾 Save State Pension Data", type="primary"):
        pension_data.update({
            'state_pension_enabled': True,
            'date_of_birth': date_of_birth.strftime('%Y-%m-%d'),
            'state_pension_ni_years': ni_years,
            'state_pension_projected_years': projected_future_years,
            'state_pension_annual_amount': forecast['annual_amount'],
            'target_retirement_age': pension_age
        })
        save_pension_plan(pension_data, user_id)
        st.success("✅ State Pension data saved!")
        st.rerun()
    
    # ========================================================================
    # SPOUSE STATE PENSION
    # ========================================================================
    st.markdown("---")
    st.markdown("---")
    st.subheader("👥 Spouse/Partner State Pension")
    
    include_spouse = st.checkbox(
        "Include Spouse/Partner State Pension",
        value=pension_data.get('spouse_state_pension_enabled', False),
        help="Add your spouse's State Pension to household retirement planning"
    )
    
    if include_spouse:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Spouse date of birth
            spouse_dob_str = pension_data.get('spouse_date_of_birth')
            if spouse_dob_str:
                spouse_dob = datetime.strptime(spouse_dob_str, '%Y-%m-%d').date()
            else:
                spouse_dob = date(1980, 1, 1)
            
            spouse_date_of_birth = st.date_input(
                "Spouse Date of Birth",
                value=spouse_dob,
                min_value=date(1940, 1, 1),
                max_value=date.today(),
                key="spouse_dob",
                help="Your spouse's date of birth"
            )
            
            # Calculate spouse State Pension age
            spouse_pension_age = calculate_state_pension_age(spouse_date_of_birth)
            spouse_current_age = (date.today() - spouse_date_of_birth).days // 365
            spouse_years_to_pension = max(0, spouse_pension_age - spouse_current_age)
            
            st.info(f"📅 Spouse's State Pension age is **{spouse_pension_age}** (in {spouse_years_to_pension} years)")
            
            # Spouse NI years
            col_a, col_b = st.columns(2)
            
            with col_a:
                spouse_ni_years = st.number_input(
                    "Spouse Current NI Years",
                    min_value=0,
                    max_value=50,
                    value=pension_data.get('spouse_state_pension_ni_years', 0),
                    key="spouse_ni_years",
                    help="Spouse's NI qualifying years"
                )
            
            with col_b:
                spouse_employment_status = st.selectbox(
                    "Spouse Employment Status",
                    ["Employed", "Self-Employed", "Unemployed (claiming credits)", "Not working"],
                    key="spouse_employment",
                    help="This affects future NI contributions"
                )
            
            # Project spouse future years
            if spouse_employment_status in ["Employed", "Self-Employed"]:
                spouse_projected_future_years = spouse_years_to_pension
            elif spouse_employment_status == "Unemployed (claiming credits)":
                spouse_projected_future_years = int(spouse_years_to_pension * 0.8)
            else:
                spouse_projected_future_years = st.number_input(
                    "Spouse Expected Future Qualifying Years",
                    min_value=0,
                    max_value=spouse_years_to_pension,
                    value=0,
                    key="spouse_projected_years",
                    help="Years spouse expects to contribute NI"
                )
            
            # Calculate spouse forecast
            spouse_forecast = forecast_state_pension(spouse_date_of_birth, spouse_ni_years, spouse_projected_future_years)
        
        with col2:
            st.markdown("### Spouse's State Pension")
            
            if spouse_ni_years > 0:
                tab_current, tab_projected = st.tabs(["📊 Current", "🎯 At Retirement"])
                
                with tab_current:
                    spouse_current_amount = calculate_state_pension_amount(spouse_ni_years)
                    spouse_current_monthly = spouse_current_amount / 12
                    
                    st.metric("NI Years Accrued", f"{spouse_ni_years} years")
                    st.metric("Current Annual", f"£{spouse_current_amount:,.2f}")
                    st.metric("Current Monthly", f"£{spouse_current_monthly:,.2f}")
                    
                    spouse_current_progress = min(spouse_ni_years / QUALIFYING_YEARS_FULL, 1.0)
                    st.progress(spouse_current_progress)
                    st.caption(f"{spouse_current_progress*100:.0f}% of full pension")
                
                with tab_projected:
                    st.metric(
                        "Projected Total Years",
                        f"{spouse_forecast['qualifying_years']} years",
                        delta=f"+{spouse_projected_future_years} years"
                    )
                    st.metric("Projected Annual", f"£{spouse_forecast['annual_amount']:,.2f}")
                    st.metric("Projected Monthly", f"£{spouse_forecast['monthly_amount']:,.2f}")
                    
                    spouse_progress = min(spouse_forecast['qualifying_years'] / QUALIFYING_YEARS_FULL, 1.0)
                    st.progress(spouse_progress)
                    
                    if spouse_forecast['is_full_pension']:
                        st.success("✅ Full State Pension")
                    elif spouse_forecast['qualifying_years'] >= QUALIFYING_YEARS_MIN:
                        spouse_missing = QUALIFYING_YEARS_FULL - spouse_forecast['qualifying_years']
                        st.warning(f"⚠️ {spouse_missing} more years for full")
                    else:
                        spouse_need = QUALIFYING_YEARS_MIN - spouse_forecast['qualifying_years']
                        st.error(f"❌ Need {spouse_need} more years to qualify")
            else:
                st.metric("Total Qualifying Years", f"{spouse_forecast['qualifying_years']}")
                st.metric("Annual Pension", f"£{spouse_forecast['annual_amount']:,.2f}")
                st.metric("Monthly Pension", f"£{spouse_forecast['monthly_amount']:,.2f}")
                
                spouse_progress = min(spouse_forecast['qualifying_years'] / QUALIFYING_YEARS_FULL, 1.0)
                st.progress(spouse_progress)
        
        # Household total
        st.markdown("---")
        st.markdown("### 🏠 Household State Pension Total")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            primary_annual = forecast['annual_amount']
            st.metric("Your Annual Pension", f"£{primary_annual:,.2f}")
        with col2:
            spouse_annual = spouse_forecast['annual_amount']
            st.metric("Spouse Annual Pension", f"£{spouse_annual:,.2f}")
        with col3:
            household_total = primary_annual + spouse_annual
            st.metric("Household Total", f"£{household_total:,.2f}", 
                     help="Combined annual State Pension income")
        
        # Save spouse data
        if st.button("💾 Save Spouse State Pension Data", type="primary", key="save_spouse_sp"):
            pension_data.update({
                'spouse_state_pension_enabled': True,
                'spouse_date_of_birth': spouse_date_of_birth.strftime('%Y-%m-%d'),
                'spouse_state_pension_ni_years': spouse_ni_years,
                'spouse_state_pension_projected_years': spouse_projected_future_years,
                'spouse_state_pension_annual_amount': spouse_forecast['annual_amount'],
                'spouse_retirement_age': spouse_pension_age,
                'spouse_age': spouse_current_age
            })
            save_pension_plan(pension_data, user_id)
            st.success("✅ Spouse State Pension data saved!")
            st.rerun()


def show_uss_pension_calculator(pension_data, user_id):
    """USS pension calculator"""
    
    st.subheader("🎓 USS Pension Calculator")
    
    st.info("""
    The Universities Superannuation Scheme (USS) is a pension scheme for UK universities.
    It builds up pension at a rate of 1/85th of your salary for each year of membership.
    """)
    
    # Check if user wants to use USS
    use_uss = st.checkbox(
        "I am a member of USS",
        value=pension_data.get('uss_enabled', False)
    )
    
    if not use_uss:
        st.warning("💡 If you work for a UK university, you may be eligible for USS pension benefits")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Current situation
        st.markdown("### Current USS Details")
        
        current_salary = st.number_input(
            "Current Annual Salary (£)",
            min_value=0,
            value=int(pension_data.get('uss_current_salary', 50000)),
            step=1000,
            help="Your pensionable salary"
        )
        
        years_in_scheme = st.number_input(
            "Years in USS",
            min_value=0.0,
            max_value=50.0,
            value=float(pension_data.get('uss_years_in_scheme', 0)),
            step=0.5,
            help="Total years of USS membership"
        )
        
        # Additional Voluntary Contributions (AVC)
        st.markdown("---")
        st.markdown("### Additional Voluntary Contributions (AVC)")
        
        use_avc = st.checkbox(
            "I make Additional Voluntary Contributions",
            value=pension_data.get('uss_avc_enabled', False),
            help="AVCs are invested separately and can boost your retirement income"
        )
        
        avc_amount = 0
        avc_percentage = 0
        if use_avc:
            col_avc1, col_avc2 = st.columns(2)
            
            with col_avc1:
                avc_percentage = st.slider(
                    "AVC as % of Salary",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(pension_data.get('uss_avc_percentage', 0)),
                    step=0.5,
                    help="Additional contributions beyond standard USS"
                )
                avc_amount = (current_salary * avc_percentage / 100) if current_salary > 0 else 0
            
            with col_avc2:
                st.metric(
                    "Annual AVC",
                    f"£{avc_amount:,.2f}",
                    help="This goes into your USS AVC investment fund"
                )
                st.metric(
                    "Monthly AVC",
                    f"£{avc_amount/12:,.2f}"
                )
            
            st.info("💡 **AVC Integration**: Your AVCs are invested in the USS Investment Builder, which offers different fund options and can provide flexible retirement income. These are separate from your main USS pension benefit.")
        
        # Calculate current contributions
        contributions = calculate_uss_contributions(current_salary, years_in_scheme, avc_amount)
        
        st.markdown("### Monthly Contributions")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("Your Contribution", f"£{contributions['employee_monthly']:,.2f}")
            st.caption(f"{contributions['employee_rate']:.1f}% of salary")
        
        with col_b:
            st.metric("Employer Contribution", f"£{contributions['employer_monthly']:,.2f}")
            st.caption(f"{contributions['employer_rate']:.1f}% of salary")
        
        with col_c:
            st.metric("Total Monthly", f"£{contributions['total_monthly']:,.2f}")
            st.caption(f"{contributions['total_rate']:.1f}% of salary")
        
        if use_avc and avc_amount > 0:
            st.markdown("### Total Including AVC")
            col_d, col_e = st.columns(2)
            
            with col_d:
                total_with_avc = contributions['total_monthly'] + contributions['avc_monthly']
                st.metric(
                    "Total Monthly (USS + AVC)",
                    f"£{total_with_avc:,.2f}",
                    help="Combined USS pension and AVC contributions"
                )
            
            with col_e:
                total_rate_with_avc = contributions['total_rate'] + contributions['avc_rate']
                st.metric(
                    "Total Rate",
                    f"{total_rate_with_avc:.1f}%",
                    help="Combined percentage of salary"
                )
        
        # Future projection
        st.markdown("---")
        st.markdown("### Retirement Projection")
        
        current_age = pension_data.get('current_age', 30)
        if not current_age:
            current_age = 30
        
        retirement_age = st.slider(
            "Target Retirement Age",
            min_value=55,
            max_value=75,
            value=USS_RETIREMENT_AGE,
            help="Age you plan to retire"
        )
        
        salary_growth = st.slider(
            "Expected Annual Salary Growth",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.5,
            help="Expected average annual salary increase"
        ) / 100
        
        # Project pension
        projection = project_uss_pension(
            current_salary,
            current_age,
            years_in_scheme,
            retirement_age,
            salary_growth
        )
        
        # Calculate current position (if already in scheme)
        if years_in_scheme > 0:
            current_pension = calculate_current_uss_pension_value(current_salary, years_in_scheme)
        else:
            current_pension = None
        
        # Project AVC if enabled
        avc_projection = None
        current_avc_value = 0
        if use_avc and avc_amount > 0:
            current_avc_value = st.number_input(
                "Current AVC Pot Value (£)",
                min_value=0,
                value=int(pension_data.get('uss_avc_current_value', 0)),
                step=1000,
                help="Your current AVC investment builder balance"
            )
            
            avc_growth_rate = st.slider(
                "Expected AVC Growth Rate",
                min_value=0.0,
                max_value=15.0,
                value=5.0,
                step=0.5,
                help="Expected annual investment return on AVCs"
            ) / 100
            
            avc_projection = project_avc_growth(
                current_avc_value,
                avc_amount,
                retirement_age - current_age,
                avc_growth_rate
            )
    
    with col2:
        st.markdown("### Your USS Pension")
        
        # Show current vs projected in tabs
        if current_pension and years_in_scheme > 0:
            tab_current, tab_projected = st.tabs(["📊 Current Position", "🎯 At Retirement"])
            
            with tab_current:
                st.markdown("**Accrued So Far**")
                st.metric(
                    "Current Annual Pension",
                    f"£{current_pension['annual_pension']:,.2f}",
                    help=f"Based on {years_in_scheme:.1f} years of service"
                )
                st.metric(
                    "Current Monthly Pension",
                    f"£{current_pension['monthly_pension']:,.2f}"
                )
                st.metric(
                    "Current Lump Sum Available",
                    f"£{current_pension['lump_sum_available']:,.2f}"
                )
                
                if use_avc and avc_projection:
                    st.markdown("---")
                    st.markdown("**Current AVC Pot**")
                    st.metric(
                        "AVC Balance",
                        f"£{avc_projection['current_value']:,.2f}"
                    )
            
            with tab_projected:
                st.markdown(f"**At Age {retirement_age}**")
                st.metric(
                    "Projected Annual Pension",
                    f"£{projection['annual_pension']:,.2f}",
                    delta=f"+£{projection['annual_pension'] - current_pension['annual_pension']:,.0f}"
                )
                st.metric(
                    "Projected Monthly Pension",
                    f"£{projection['monthly_pension']:,.2f}"
                )
                st.metric(
                    "Tax-Free Lump Sum",
                    f"£{projection['lump_sum_available']:,.2f}"
                )
                
                if use_avc and avc_projection:
                    st.markdown("---")
                    st.markdown("**Projected AVC Pot**")
                    st.metric(
                        "AVC Total at Retirement",
                        f"£{avc_projection['projected_value']:,.2f}",
                        delta=f"+£{avc_projection['projected_value'] - avc_projection['current_value']:,.0f}"
                    )
                    st.metric(
                        "Annual Income (4% rule)",
                        f"£{avc_projection['annual_drawdown_4pct']:,.2f}"
                    )
                    st.caption(f"Growth: £{avc_projection['investment_growth']:,.0f} | Contributions: £{avc_projection['total_contributions']:,.0f}")
        else:
            # No current pension yet, just show projection
            st.metric(
                "Annual Pension",
                f"£{projection['annual_pension']:,.2f}",
                f"at age {retirement_age}"
            )
            st.metric(
                "Monthly Pension",
                f"£{projection['monthly_pension']:,.2f}"
            )
            st.metric(
                "Tax-Free Lump Sum",
                f"£{projection['lump_sum_available']:,.2f}",
                "3x annual pension"
            )
            
            if use_avc and avc_projection:
                st.markdown("---")
                st.markdown("**AVC Pot at Retirement**")
                st.metric(
                    "Projected AVC Value",
                    f"£{avc_projection['projected_value']:,.2f}"
                )
                st.metric(
                    "Annual Income (4% rule)",
                    f"£{avc_projection['annual_drawdown_4pct']:,.2f}"
                )
        
        st.metric(
            "Total Years in Scheme",
            f"{projection['total_years_in_scheme']:.1f} years"
        )
    
    # Detailed breakdown
    st.markdown("---")
    st.markdown("### Projection Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Salary", f"£{projection['current_salary']:,.2f}")
    
    with col2:
        st.metric("Final Salary", f"£{projection['final_salary']:,.2f}")
    
    with col3:
        st.metric("Salary Growth", f"{projection['salary_growth_rate']*100:.1f}%/year")
    
    st.info(f"""
    💡 **How USS works:** You build up 1/85th of your salary for each year of membership.
    With {projection['total_years_in_scheme']:.1f} years, you'll get {projection['total_years_in_scheme']/85:.2%} of your final salary as pension.
    """)
    
    # Save button
    if st.button("💾 Save USS Data", type="primary"):
        pension_data.update({
            'uss_enabled': True,
            'uss_current_salary': current_salary,
            'uss_years_in_scheme': years_in_scheme,
            'uss_projected_annual_pension': projection['annual_pension'],
            'uss_projected_lump_sum': projection['lump_sum_available'],
            'uss_avc_enabled': use_avc,
            'uss_avc_annual_amount': avc_amount,
            'uss_avc_percentage': avc_percentage if use_avc else 0,
            'uss_avc_current_value': current_avc_value if use_avc and avc_amount > 0 else 0,
            'uss_avc_projected_value': avc_projection['projected_value'] if avc_projection else 0,
            'target_retirement_age': retirement_age,
            'salary_growth_rate': salary_growth
        })
        save_pension_plan(pension_data, user_id)
        st.success("✅ USS data saved!")
        st.rerun()
    
    # ========================================================================
    # SPOUSE USS PENSION
    # ========================================================================
    st.markdown("---")
    st.markdown("---")
    st.subheader("👥 Spouse/Partner USS Pension")
    
    spouse_use_uss = st.checkbox(
        "Spouse is a member of USS",
        value=pension_data.get('spouse_uss_enabled', False),
        key="spouse_uss_enabled"
    )
    
    if spouse_use_uss:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            spouse_salary = st.number_input(
                "Spouse Annual Salary (£)",
                min_value=0,
                value=int(pension_data.get('spouse_uss_current_salary', 50000)),
                step=1000,
                key="spouse_uss_salary"
            )
            
            spouse_uss_years = st.number_input(
                "Spouse Years in USS",
                min_value=0.0,
                max_value=50.0,
                value=float(pension_data.get('spouse_uss_years_in_scheme', 0)),
                step=0.5,
                key="spouse_uss_years"
            )
            
            spouse_uss_avc = st.checkbox(
                "Spouse makes AVCs",
                value=pension_data.get('spouse_uss_avc_enabled', False),
                key="spouse_uss_avc"
            )
            
            spouse_avc_amount = 0
            if spouse_uss_avc:
                spouse_avc_pct = st.slider(
                    "Spouse AVC %",
                    0.0, 20.0,
                    float(pension_data.get('spouse_uss_avc_percentage', 0)),
                    0.5,
                    key="spouse_avc_pct"
                )
                spouse_avc_amount = spouse_salary * (spouse_avc_pct / 100)
                spouse_avc_current = st.number_input(
                    "Current AVC Value (£)",
                    0,
                    value=int(pension_data.get('spouse_uss_avc_current_value', 0)),
                    step=1000,
                    key="spouse_avc_current"
                )
        
        with col2:
            # Simple projection
            spouse_annual_pension = spouse_uss_years * spouse_salary * USS_ACCRUAL_RATE
            spouse_lump_sum = spouse_annual_pension * USS_LUMP_SUM_MULTIPLE
            
            st.metric("Current USS Pension", f"£{spouse_annual_pension:,.0f}/year")
            st.metric("Available Lump Sum", f"£{spouse_lump_sum:,.0f}")
            if spouse_uss_avc:
                st.metric("AVC Annual Contribution", f"£{spouse_avc_amount:,.0f}")
        
        if st.button("💾 Save Spouse USS Data", type="primary", key="save_spouse_uss"):
            pension_data.update({
                'spouse_uss_enabled': True,
                'spouse_uss_current_salary': spouse_salary,
                'spouse_uss_years_in_scheme': spouse_uss_years,
                'spouse_uss_projected_annual_pension': spouse_annual_pension,
                'spouse_uss_projected_lump_sum': spouse_lump_sum,
                'spouse_uss_avc_enabled': spouse_uss_avc,
                'spouse_uss_avc_annual_amount': spouse_avc_amount if spouse_uss_avc else 0,
                'spouse_uss_avc_current_value': spouse_avc_current if spouse_uss_avc else 0
            })
            save_pension_plan(pension_data, user_id)
            st.success("✅ Spouse USS data saved!")
            st.rerun()


def show_sipp_calculator(pension_data, user_id):
    """SIPP calculator and tracker"""
    
    st.subheader("💰 SIPP (Self-Invested Personal Pension)")
    
    st.info("""
    A SIPP is a personal pension you control. You get tax relief on contributions,
    and your money grows tax-free. You can access it from age 55 (rising to 57 in 2028).
    """)
    
    use_sipp = st.checkbox(
        "I have a SIPP or want to plan for one",
        value=pension_data.get('sipp_enabled', False)
    )
    
    if not use_sipp:
        st.warning("💡 A SIPP can be a powerful way to supplement your State Pension and workplace pension")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Current SIPP Details")
        
        current_value = st.number_input(
            "Current SIPP Value (£)",
            min_value=0,
            value=int(pension_data.get('sipp_current_value', 0)),
            step=1000,
            help="Current value of your SIPP pot"
        )
        
        annual_contribution = st.number_input(
            "Annual Contribution (£)",
            min_value=0,
            max_value=SIPP_ANNUAL_ALLOWANCE,
            value=int(pension_data.get('sipp_annual_contribution', 0)),
            step=500,
            help=f"Annual allowance is £{SIPP_ANNUAL_ALLOWANCE:,.0f}"
        )
        
        # Tax relief calculation
        if annual_contribution > 0:
            income = st.number_input(
                "Your Annual Income (£)",
                min_value=0,
                value=50000,
                step=1000,
                help="Used to calculate tax relief"
            )
            
            tax_relief = calculate_sipp_tax_relief(annual_contribution, income)
            
            st.markdown("### Tax Relief on Contributions")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.metric("Your Cost", f"£{tax_relief['net_cost']:,.2f}")
            
            with col_b:
                st.metric("Tax Relief", f"£{tax_relief['total_tax_relief']:,.2f}")
                st.caption(f"{tax_relief['tax_bracket']}")
            
            with col_c:
                st.metric("Pension Gets", f"£{tax_relief['gross_contribution']:,.2f}")
                st.caption(f"+{tax_relief['effective_bonus']:.0f}% bonus")
        
        # Growth projection
        st.markdown("---")
        st.markdown("### Retirement Projection")
        
        current_age = pension_data.get('current_age', 30)
        if not current_age:
            current_age = 30
        
        retirement_age = st.slider(
            "Retirement Age",
            min_value=55,
            max_value=75,
            value=pension_data.get('target_retirement_age', 67)
        )
        
        years_to_retirement = max(0, retirement_age - current_age)
        
        growth_rate = st.slider(
            "Expected Growth Rate",
            min_value=0.0,
            max_value=12.0,
            value=5.0,
            step=0.5,
            help="Expected average annual return"
        ) / 100
        
        # Project SIPP growth
        projection = project_sipp_growth(
            annual_contribution,
            years_to_retirement,
            growth_rate,
            current_value
        )
    
    with col2:
        st.markdown("### At Retirement")
        
        st.metric(
            "Total SIPP Value",
            f"£{projection['final_value']:,.0f}"
        )
        
        st.metric(
            "Tax-Free Lump Sum",
            f"£{projection['tax_free_lump_sum']:,.0f}",
            "25% tax-free"
        )
        
        st.metric(
            "Remaining Pot",
            f"£{projection['remaining_pot']:,.0f}",
            "For drawdown/annuity"
        )
        
        # Annual income from remaining pot (4% rule)
        annual_income = projection['remaining_pot'] * 0.04
        st.metric(
            "Annual Income",
            f"£{annual_income:,.0f}",
            "@ 4% withdrawal rate"
        )
    
    # Breakdown
    st.markdown("---")
    st.markdown("### Growth Breakdown")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Starting Value", f"£{current_value:,.0f}")
    
    with col2:
        st.metric("Total Contributions", f"£{projection['total_contributions']:,.0f}")
    
    with col3:
        st.metric("Investment Growth", f"£{projection['total_growth']:,.0f}")
    
    # Growth chart
    if years_to_retirement > 0:
        df = pd.DataFrame({
            'Year': range(years_to_retirement + 1),
            'Value': projection['values_by_year']
        })
        st.line_chart(df.set_index('Year'), height=300)
    
    # Save button
    if st.button("💾 Save SIPP Data", type="primary"):
        pension_data.update({
            'sipp_enabled': True,
            'sipp_current_value': current_value,
            'sipp_annual_contribution': annual_contribution,
            'sipp_projected_value': projection['final_value'],
            'sipp_growth_rate': growth_rate,
            'target_retirement_age': retirement_age
        })
        save_pension_plan(pension_data, user_id)
        st.success("✅ SIPP data saved!")
        st.rerun()
    
    # ========================================================================
    # SPOUSE SIPP
    # ========================================================================
    st.markdown("---")
    st.markdown("---")
    st.subheader("👥 Spouse/Partner SIPP")
    
    spouse_use_sipp = st.checkbox(
        "Spouse has a SIPP",
        value=pension_data.get('spouse_sipp_enabled', False),
        key="spouse_sipp_enabled"
    )
    
    if spouse_use_sipp:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            spouse_sipp_current = st.number_input(
                "Spouse Current SIPP Value (£)",
                min_value=0,
                value=int(pension_data.get('spouse_sipp_current_value', 0)),
                step=1000,
                key="spouse_sipp_current"
            )
            
            spouse_sipp_contribution = st.number_input(
                "Spouse Annual Contribution (£)",
                min_value=0,
                value=int(pension_data.get('spouse_sipp_annual_contribution', 0)),
                step=500,
                key="spouse_sipp_contribution"
            )
            
            spouse_sipp_growth = st.slider(
                "Spouse Expected Growth Rate (%)",
                0.0, 15.0,
                float(pension_data.get('spouse_sipp_growth_rate', 5.0)),
                0.5,
                key="spouse_sipp_growth"
            )
        
        with col2:
            # Simple projection
            years_to_retirement = max(1, pension_data.get('spouse_retirement_age', 67) - pension_data.get('spouse_age', 30))
            spouse_sipp_projected = project_sipp_growth(
                spouse_sipp_current,
                spouse_sipp_contribution,
                spouse_sipp_growth / 100,
                years_to_retirement
            )
            
            st.metric("Projected at Retirement", f"£{spouse_sipp_projected['final_value']:,.0f}")
            st.metric("Tax-Free Lump Sum", f"£{spouse_sipp_projected['tax_free_lump_sum']:,.0f}")
        
        if st.button("💾 Save Spouse SIPP Data", type="primary", key="save_spouse_sipp"):
            pension_data.update({
                'spouse_sipp_enabled': True,
                'spouse_sipp_current_value': spouse_sipp_current,
                'spouse_sipp_annual_contribution': spouse_sipp_contribution,
                'spouse_sipp_projected_value': spouse_sipp_projected['final_value'],
                'spouse_sipp_growth_rate': spouse_sipp_growth / 100
            })
            save_pension_plan(pension_data, user_id)
            st.success("✅ Spouse SIPP data saved!")
            st.rerun()


def show_retirement_income_planner(pension_data, user_id):
    """Plan total retirement income and sustainability"""
    
    st.subheader("📈 Retirement Income Planner")
    
    # Get all pension sources
    state_pension = pension_data.get('state_pension_annual_amount', 0)
    uss_pension = pension_data.get('uss_projected_annual_pension', 0)
    sipp_value = pension_data.get('sipp_projected_value', 0)
    
    retirement_age = pension_data.get('target_retirement_age', 67)
    current_age = pension_data.get('current_age', 30)
    
    if not current_age:
        current_age = 30
    
    # Life expectancy
    life_expectancy = st.slider(
        "Plan until age",
        min_value=retirement_age + 1,
        max_value=100,
        value=90,
        help="Life expectancy for planning purposes"
    )
    
    years_in_retirement = life_expectancy - retirement_age
    
    # Annual withdrawal from SIPP
    st.markdown("### SIPP Drawdown Strategy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        drawdown_strategy = st.radio(
            "Withdrawal Strategy",
            ["Safe Rate (4%)", "Custom Amount", "Make it Last"]
        )
        
        if drawdown_strategy == "Safe Rate (4%)":
            sipp_annual_withdrawal = sipp_value * 0.04
        elif drawdown_strategy == "Custom Amount":
            sipp_annual_withdrawal = st.number_input(
                "Annual Withdrawal (£)",
                min_value=0,
                value=int(sipp_value * 0.04) if sipp_value > 0 else 0,
                step=1000
            )
        else:  # Make it Last
            safe_amount = safe_withdrawal_rate(sipp_value, years_in_retirement, 0.04)
            sipp_annual_withdrawal = safe_amount
            st.info(f"💡 Calculated to last {years_in_retirement} years: £{safe_amount:,.0f}/year")
    
    with col2:
        # Test sustainability
        if sipp_value > 0 and sipp_annual_withdrawal > 0:
            drawdown = calculate_pension_drawdown(
                sipp_value,
                sipp_annual_withdrawal,
                years_in_retirement,
                0.04
            )
            
            if drawdown['is_sustainable']:
                st.success(f"✅ Sustainable for {years_in_retirement} years")
            else:
                st.error(f"❌ Will run out after {drawdown['years_sustainable']} years")
            
            st.metric("Withdrawal Rate", f"{drawdown['withdrawal_rate']:.2f}%")
    
    # Total income
    st.markdown("---")
    st.markdown("### Total Retirement Income")
    
    total_income = calculate_total_retirement_income(
        state_pension,
        uss_pension,
        sipp_annual_withdrawal
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("State Pension", f"£{total_income['state_pension_annual']:,.0f}/year")
    
    with col2:
        st.metric("USS Pension", f"£{total_income['uss_pension_annual']:,.0f}/year")
    
    with col3:
        st.metric("SIPP Drawdown", f"£{total_income['sipp_drawdown_annual']:,.0f}/year")
    
    with col4:
        st.metric("Total Income", f"£{total_income['total_annual']:,.0f}/year")
    
    # Monthly budget
    st.info(f"💰 **Monthly Budget:** £{total_income['total_monthly']:,.2f}")
    
    # Income composition
    if total_income['total_annual'] > 0:
        fig = create_pension_pie_chart(
            state_pension,
            uss_pension,
            sipp_annual_withdrawal,
            pension_data.get('uss_avc_projected_value', 0) * 0.04
        )
        st.plotly_chart(fig, use_container_width=True, key="retirement_income_pie_chart")
    
    # Compare to desired income
    desired_income = st.number_input(
        "Desired Annual Retirement Income (£)",
        min_value=0,
        value=int(pension_data.get('desired_retirement_income', 30000)),
        step=1000
    )
    
    if desired_income > 0:
        coverage = (total_income['total_annual'] / desired_income) * 100
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.progress(min(coverage / 100, 1.0))
            
            if coverage >= 100:
                surplus = total_income['total_annual'] - desired_income
                st.success(f"✅ You'll have £{surplus:,.0f}/year surplus!")
            else:
                shortfall = desired_income - total_income['total_annual']
                st.warning(f"⚠️ Shortfall of £{shortfall:,.0f}/year ({100-coverage:.0f}%)")
        
        with col2:
            st.metric("Income Coverage", f"{coverage:.0f}%")
    
    # Save plan
    if st.button("💾 Save Retirement Plan", type="primary"):
        pension_data.update({
            'desired_retirement_income': desired_income,
            'expected_total_pension_income': total_income['total_annual'],
            'drawdown_rate': sipp_annual_withdrawal / sipp_value if sipp_value > 0 else 0.04
        })
        save_pension_plan(pension_data, user_id)
        st.success("✅ Retirement plan saved!")


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def load_pension_plan(user_id):
    """Load user's pension plan from database"""
    db = SessionLocal()
    try:
        plan = db.query(PensionPlan).filter(
            PensionPlan.user_id == user_id,
            PensionPlan.is_active == True
        ).order_by(PensionPlan.created_at.desc()).first()
        
        if plan:
            return {
                'id': plan.id,
                'date_of_birth': plan.date_of_birth,
                'target_retirement_age': plan.target_retirement_age,
                'state_pension_enabled': plan.state_pension_enabled,
                'state_pension_ni_years': plan.state_pension_ni_years,
                'state_pension_projected_years': plan.state_pension_projected_years,
                'state_pension_annual_amount': plan.state_pension_annual_amount,
                'uss_enabled': plan.uss_enabled,
                'uss_current_salary': plan.uss_current_salary,
                'uss_years_in_scheme': plan.uss_years_in_scheme,
                'uss_projected_annual_pension': plan.uss_projected_annual_pension,
                'uss_projected_lump_sum': plan.uss_projected_lump_sum,
                'uss_avc_enabled': plan.uss_avc_enabled,
                'uss_avc_annual_amount': plan.uss_avc_annual_amount,
                'uss_avc_percentage': plan.uss_avc_percentage,
                'uss_avc_current_value': plan.uss_avc_current_value,
                'uss_avc_projected_value': plan.uss_avc_projected_value,
                'sipp_enabled': plan.sipp_enabled,
                'sipp_current_value': plan.sipp_current_value,
                'sipp_annual_contribution': plan.sipp_annual_contribution,
                'sipp_projected_value': plan.sipp_projected_value,
                'sipp_growth_rate': plan.sipp_growth_rate,
                'desired_retirement_income': plan.desired_retirement_income,
                'expected_total_pension_income': plan.expected_total_pension_income,
                'simulation_end_age': plan.simulation_end_age,
                'salary_growth_rate': plan.salary_growth_rate,
                'drawdown_rate': plan.drawdown_rate,
                'current_age': (date.today() - datetime.strptime(plan.date_of_birth, '%Y-%m-%d').date()).days // 365 if plan.date_of_birth else None
            }
        else:
            # Return empty plan
            return {
                'state_pension_enabled': False,
                'uss_enabled': False,
                'uss_avc_enabled': False,
                'uss_avc_annual_amount': 0,
                'uss_avc_percentage': 0,
                'uss_avc_current_value': 0,
                'uss_avc_projected_value': 0,
                'sipp_enabled': False,
                'target_retirement_age': 67,
                'simulation_end_age': 87,
                'salary_growth_rate': 0.02,
                'sipp_growth_rate': 0.05,
                'drawdown_rate': 0.04
            }
    finally:
        db.close()


def save_pension_plan(pension_data, user_id):
    """Save pension plan to database"""
    db = SessionLocal()
    try:
        # Check if plan exists
        plan = db.query(PensionPlan).filter(
            PensionPlan.user_id == user_id,
            PensionPlan.is_active == True
        ).first()
        
        if plan:
            # Update existing
            for key, value in pension_data.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            plan.last_calculated = datetime.now()
        else:
            # Create new
            plan = PensionPlan(
                user_id=user_id,
                **{k: v for k, v in pension_data.items() if k != 'id' and k != 'current_age'}
            )
            db.add(plan)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        st.error(f"Error saving pension plan: {str(e)}")
        return False
    finally:
        db.close()
