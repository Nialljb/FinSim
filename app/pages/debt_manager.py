"""
Debt Manager UI for FinSim
Track and manage debts with amortization analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

from services.debt_manager import (
    calculate_monthly_payment,
    generate_amortization_schedule,
    calculate_payoff_date,
    compare_payoff_strategies,
    calculate_debt_to_income_ratio,
    calculate_credit_utilization,
    create_payoff_comparison_chart,
    create_amortization_chart,
    create_payment_breakdown_chart
)

from data_layer.database import (
    get_user_debts,
    create_debt,
    update_debt,
    delete_debt
)

from services.currency_manager import (
    format_currency,
    to_base_currency,
    from_base_currency
)


def show_debt_manager(user_id):
    """Main debt manager interface"""
    
    st.title("💳 Debt Manager")
    
    st.markdown("""
    Track and manage all your debts in one place. Visualize amortization schedules, 
    compare payoff strategies, and optimize your debt repayment plan.
    """)
    
    # Get user's selected currency from session state
    selected_currency = st.session_state.get('selected_currency', 'EUR')
    
    # Currency symbols mapping
    CURRENCY_SYMBOLS = {
        'EUR': '€', 'GBP': '£', 'USD': '$', 'CAD': 'C$', 'AUD': 'A$', 
        'NZD': 'NZ$', 'CHF': 'CHF', 'SEK': 'kr', 'NOK': 'kr', 'DKK': 'kr',
        'JPY': '¥', 'CNY': '¥', 'INR': '₹', 'SGD': 'S$', 'HKD': 'HK$'
    }
    currency_symbol = CURRENCY_SYMBOLS.get(selected_currency, '€')
    
    # Create tabs for different sections
    debt_tabs = st.tabs([
        "📊 Overview",
        "➕ Add Debt",
        "📈 Amortization",
        "🎯 Payoff Strategies"
    ])
    
    # ========================================================================
    # TAB 1: OVERVIEW
    # ========================================================================
    with debt_tabs[0]:
        show_debt_overview(user_id, selected_currency, currency_symbol)
    
    # ========================================================================
    # TAB 2: ADD DEBT
    # ========================================================================
    with debt_tabs[1]:
        show_add_debt(user_id, selected_currency, currency_symbol)
    
    # ========================================================================
    # TAB 3: AMORTIZATION
    # ========================================================================
    with debt_tabs[2]:
        show_amortization_analysis(user_id, selected_currency, currency_symbol)
    
    # ========================================================================
    # TAB 4: PAYOFF STRATEGIES
    # ========================================================================
    with debt_tabs[3]:
        show_payoff_strategies(user_id, selected_currency, currency_symbol)


def show_debt_overview(user_id, selected_currency, currency_symbol):
    """Overview dashboard showing all debts"""
    
    st.subheader("Your Debts Overview")
    
    # Get user's debts
    debts = get_user_debts(user_id)
    
    if not debts:
        st.info("📝 No debts tracked yet. Add your first debt in the 'Add Debt' tab.")
        return
    
    # Calculate totals
    total_balance = sum(from_base_currency(d.current_balance, selected_currency) for d in debts)
    total_monthly = sum(from_base_currency(d.monthly_payment, selected_currency) for d in debts)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Debt", format_currency(total_balance, selected_currency))
    
    with col2:
        st.metric("Monthly Payments", format_currency(total_monthly, selected_currency))
    
    with col3:
        st.metric("Number of Debts", len(debts))
    
    with col4:
        avg_rate = np.average([d.interest_rate for d in debts], 
                             weights=[d.current_balance for d in debts]) * 100
        st.metric("Weighted Avg Rate", f"{avg_rate:.2f}%")
    
    st.markdown("---")
    
    # Debt breakdown table
    st.subheader("Debt Details")
    
    debt_data = []
    for debt in debts:
        balance_display = from_base_currency(debt.current_balance, selected_currency)
        payment_display = from_base_currency(debt.monthly_payment, selected_currency)
        
        debt_data.append({
            'Name': debt.name,
            'Type': debt.debt_type.replace('_', ' ').title(),
            'Balance': format_currency(balance_display, selected_currency),
            'Rate': f"{debt.interest_rate * 100:.2f}%",
            'Monthly Payment': format_currency(payment_display, selected_currency),
            'Actions': debt.id
        })
    
    debt_df = pd.DataFrame(debt_data)
    
    # Display table without Actions column (we'll handle that separately)
    display_df = debt_df.drop('Actions', axis=1)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Debt Prioritization Guidance
    st.markdown("---")
    st.subheader("📌 Debt Prioritization Guide")
    
    st.info("""⚠️ **Disclaimer:** This tool provides general information only and is not financial advice. 
    Please consult with a qualified financial advisor for personalized guidance.""")
    
    # Sort debts by interest rate (highest first)
    sorted_debts = sorted(debts, key=lambda d: d.interest_rate, reverse=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Priority Order (by interest rate):**")
        for i, debt in enumerate(sorted_debts[:5], 1):
            rate = debt.interest_rate * 100
            balance = from_base_currency(debt.current_balance, selected_currency)
            
            # Color code by urgency
            if rate >= 15:  # High interest (credit cards, etc.)
                st.error(f"{i}. 🔴 **{debt.name}** - {rate:.1f}% ({format_currency(balance, selected_currency)})")
            elif rate >= 7:
                st.warning(f"{i}. 🟡 **{debt.name}** - {rate:.1f}% ({format_currency(balance, selected_currency)})")
            else:
                st.success(f"{i}. 🟢 **{debt.name}** - {rate:.1f}% ({format_currency(balance, selected_currency)})")
    
    with col2:
        st.markdown("**General Strategy Guidance:**")
        
        high_interest = [d for d in debts if d.interest_rate >= 0.15]
        low_interest = [d for d in debts if d.interest_rate < 0.05]
        
        if high_interest:
            st.error(f"""🔴 **High Priority:** You have {len(high_interest)} high-interest debt(s) (≥15%). 
            Focus on paying these off first - they cost you the most in interest.""")
        
        if low_interest:
            st.info(f"""💡 **Consider:** You have {len(low_interest)} low-interest debt(s) (<5%). 
            Depending on investment returns, it may be more beneficial to invest extra cash rather than 
            overpay these debts. Typical stock market returns (7-10%) may exceed your debt cost.""")
        
        st.caption("""Remember: This is general guidance. Your personal situation, risk tolerance, 
        and financial goals should guide your decisions. Consult a financial advisor.""")
    
    # Manage debts
    st.markdown("---")
    st.subheader("Manage Debts")
    
    for i, debt in enumerate(debts):
        with st.expander(f"{debt.name} - {format_currency(from_base_currency(debt.current_balance, selected_currency), selected_currency)}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**Type:** {debt.debt_type.replace('_', ' ').title()}")
                st.markdown(f"**Interest Rate:** {debt.interest_rate * 100:.2f}%")
                if debt.lender:
                    st.markdown(f"**Lender:** {debt.lender}")
            
            with col2:
                st.markdown(f"**Balance:** {format_currency(from_base_currency(debt.current_balance, selected_currency), selected_currency)}")
                st.markdown(f"**Monthly Payment:** {format_currency(from_base_currency(debt.monthly_payment, selected_currency), selected_currency)}")
                if debt.remaining_months:
                    st.markdown(f"**Remaining:** {debt.remaining_months} months")
            
            with col3:
                if st.button("🗑️ Delete", key=f"del_debt_{debt.id}", type="secondary"):
                    success, message = delete_debt(debt.id, user_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)


def show_add_debt(user_id, selected_currency, currency_symbol):
    """Add new debt form"""
    
    st.subheader("Add New Debt")
    
    with st.form("add_debt_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            debt_name = st.text_input("Debt Name*", placeholder="e.g., Student Loan, Credit Card")
            
            debt_type = st.selectbox(
                "Debt Type*",
                options=['student_loan', 'mortgage', 'personal_loan', 'credit_card', 'other'],
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            current_balance = st.number_input(
                f"Current Balance* ({currency_symbol})",
                min_value=0.0,
                value=10000.0,
                step=100.0
            )
            
            interest_rate = st.number_input(
                "Annual Interest Rate* (%)",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=0.1
            ) / 100
        
        with col2:
            lender = st.text_input("Lender/Bank", placeholder="Optional")
            
            # Calculate or input monthly payment
            payment_method = st.radio(
                "Payment Method",
                ["Calculate for me", "I know my payment"],
                horizontal=True
            )
            
            if payment_method == "Calculate for me":
                term_months = st.number_input(
                    "Loan Term (months)",
                    min_value=1,
                    max_value=360,
                    value=120,
                    step=12
                )
                monthly_payment = calculate_monthly_payment(current_balance, interest_rate, term_months)
                st.info(f"Calculated payment: {format_currency(monthly_payment, selected_currency)}/month")
            else:
                monthly_payment = st.number_input(
                    f"Monthly Payment ({currency_symbol})",
                    min_value=0.0,
                    value=200.0,
                    step=10.0
                )
                term_months = None
        
        # Additional fields based on debt type
        if debt_type == 'mortgage':
            st.markdown("**Mortgage Details**")
            mort_col1, mort_col2 = st.columns(2)
            with mort_col1:
                property_value = st.number_input(
                    f"Property Value ({currency_symbol})",
                    min_value=0.0,
                    value=300000.0,
                    step=10000.0
                )
            with mort_col2:
                down_payment = st.number_input(
                    f"Down Payment ({currency_symbol})",
                    min_value=0.0,
                    value=60000.0,
                    step=5000.0
                )
        else:
            property_value = None
            down_payment = None
        
        if debt_type == 'credit_card':
            credit_limit = st.number_input(
                f"Credit Limit ({currency_symbol})",
                min_value=0.0,
                value=10000.0,
                step=500.0
            )
        else:
            credit_limit = None
        
        notes = st.text_area("Notes", placeholder="Any additional information...")
        
        submit = st.form_submit_button("Add Debt", type="primary", use_container_width=True)
        
        if submit:
            if not debt_name:
                st.error("Please provide a debt name")
            elif current_balance <= 0:
                st.error("Balance must be greater than 0")
            else:
                # Convert to base currency
                base_balance = to_base_currency(current_balance, selected_currency)
                base_payment = to_base_currency(monthly_payment, selected_currency)
                base_property = to_base_currency(property_value, selected_currency) if property_value else None
                base_down = to_base_currency(down_payment, selected_currency) if down_payment else None
                base_limit = to_base_currency(credit_limit, selected_currency) if credit_limit else None
                
                success, result = create_debt(
                    user_id=user_id,
                    name=debt_name,
                    debt_type=debt_type,
                    current_balance=base_balance,
                    principal_amount=base_balance,
                    interest_rate=interest_rate,
                    monthly_payment=base_payment,
                    term_months=term_months,
                    remaining_months=term_months,
                    lender=lender if lender else None,
                    property_value=base_property,
                    down_payment=base_down,
                    credit_limit=base_limit,
                    notes=notes if notes else None,
                    start_date=datetime.now().strftime('%Y-%m-%d')
                )
                
                if success:
                    st.success(f"✅ {debt_name} added successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {result}")


def show_amortization_analysis(user_id, selected_currency, currency_symbol):
    """Amortization schedule analysis"""
    
    st.subheader("Amortization Analysis")
    
    # Get user's debts
    debts = get_user_debts(user_id)
    
    if not debts:
        st.info("📝 No debts to analyze. Add a debt first.")
        return
    
    # Select debt to analyze
    debt_options = {f"{d.name} ({format_currency(from_base_currency(d.current_balance, selected_currency), selected_currency)})": d for d in debts}
    selected_debt_name = st.selectbox("Select Debt to Analyze", options=list(debt_options.keys()))
    debt = debt_options[selected_debt_name]
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Debt Details")
        balance_display = from_base_currency(debt.current_balance, selected_currency)
        payment_display = from_base_currency(debt.monthly_payment, selected_currency)
        
        st.metric("Current Balance", format_currency(balance_display, selected_currency))
        st.metric("Interest Rate", f"{debt.interest_rate * 100:.2f}%")
        st.metric("Monthly Payment", format_currency(payment_display, selected_currency))
    
    with col2:
        st.markdown("### Extra Payment Analysis")
        extra_payment = st.number_input(
            f"Extra Monthly Payment ({currency_symbol})",
            min_value=0.0,
            value=0.0,
            step=50.0,
            help="Additional amount to pay each month"
        )
        
        # Convert to base currency for calculation
        base_extra = to_base_currency(extra_payment, selected_currency)
        
        # Calculate payoff with and without extra payment
        standard_payoff = calculate_payoff_date(
            debt.current_balance,
            debt.interest_rate,
            debt.monthly_payment,
            0
        )
        
        if extra_payment > 0:
            extra_payoff = calculate_payoff_date(
                debt.current_balance,
                debt.interest_rate,
                debt.monthly_payment,
                base_extra
            )
            
            if extra_payoff and standard_payoff:
                months_saved = standard_payoff['months'] - extra_payoff['months']
                interest_saved = standard_payoff['total_interest'] - extra_payoff['total_interest']
                
                st.success(f"⏱️ Save **{months_saved} months** ({months_saved/12:.1f} years)")
                st.success(f"💰 Save **{format_currency(from_base_currency(interest_saved, selected_currency), selected_currency)}** in interest")
    
    st.markdown("---")
    
    # Generate amortization schedule
    if debt.term_months:
        schedule = generate_amortization_schedule(
            debt.current_balance,
            debt.interest_rate,
            debt.term_months,
            base_extra
        )
        
        # Show charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_amort = create_amortization_chart(schedule, currency_symbol)
            st.plotly_chart(fig_amort, use_container_width=True)
        
        with col2:
            fig_breakdown = create_payment_breakdown_chart(schedule)
            st.plotly_chart(fig_breakdown, use_container_width=True)
        
        # Show schedule table (first 12 months and last 12 months)
        st.markdown("### Amortization Schedule")
        
        with st.expander("📅 View Full Schedule"):
            # Convert to display currency
            schedule_display = schedule.copy()
            for col in ['Payment', 'Principal', 'Interest', 'Extra_Payment', 'Balance', 'Cumulative_Interest']:
                schedule_display[col] = schedule_display[col].apply(
                    lambda x: format_currency(from_base_currency(x, selected_currency), selected_currency)
                )
            
            st.dataframe(schedule_display, use_container_width=True, hide_index=True)


def show_payoff_strategies(user_id, selected_currency, currency_symbol):
    """Compare different payoff strategies"""
    
    st.subheader("Debt Payoff Strategies")
    
    # Get user's debts
    debts = get_user_debts(user_id)
    
    if not debts:
        st.info("📝 No debts to analyze. Add a debt first.")
        return
    
    st.markdown("""
    Compare how different extra payment amounts affect your debt payoff timeline and total interest paid.
    """)
    
    # Select debt to analyze
    debt_options = {f"{d.name} ({format_currency(from_base_currency(d.current_balance, selected_currency), selected_currency)})": d for d in debts}
    selected_debt_name = st.selectbox("Select Debt", options=list(debt_options.keys()))
    debt = debt_options[selected_debt_name]
    
    # Extra payment options
    st.markdown("### Compare Extra Payment Scenarios")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        extra1 = st.number_input(f"Option 1 ({currency_symbol})", value=0, step=50)
    with col2:
        extra2 = st.number_input(f"Option 2 ({currency_symbol})", value=100, step=50)
    with col3:
        extra3 = st.number_input(f"Option 3 ({currency_symbol})", value=250, step=50)
    with col4:
        extra4 = st.number_input(f"Option 4 ({currency_symbol})", value=500, step=50)
    
    # Convert to base currency
    extra_options = [
        to_base_currency(extra1, selected_currency),
        to_base_currency(extra2, selected_currency),
        to_base_currency(extra3, selected_currency),
        to_base_currency(extra4, selected_currency)
    ]
    
    # Compare strategies
    comparison = compare_payoff_strategies(
        debt.current_balance,
        debt.interest_rate,
        debt.monthly_payment,
        extra_options
    )
    
    if not comparison.empty:
        # Convert back to display currency
        comparison_display = comparison.copy()
        comparison_display['Extra_Payment'] = comparison_display['Extra_Payment'].apply(
            lambda x: format_currency(from_base_currency(x, selected_currency), selected_currency)
        )
        comparison_display['Total_Paid'] = comparison_display['Total_Paid'].apply(
            lambda x: format_currency(from_base_currency(x, selected_currency), selected_currency)
        )
        comparison_display['Total_Interest'] = comparison_display['Total_Interest'].apply(
            lambda x: format_currency(from_base_currency(x, selected_currency), selected_currency)
        )
        comparison_display['Interest_Saved'] = comparison_display['Interest_Saved'].apply(
            lambda x: format_currency(from_base_currency(x, selected_currency), selected_currency)
        )
        
        # Rename columns for display
        comparison_display = comparison_display.rename(columns={
            'Extra_Payment': 'Extra Payment',
            'Months_to_Payoff': 'Months',
            'Years_to_Payoff': 'Years',
            'Total_Paid': 'Total Paid',
            'Total_Interest': 'Total Interest',
            'Interest_Saved': 'Interest Saved'
        })
        
        st.dataframe(comparison_display, use_container_width=True, hide_index=True)
        
        # Show chart
        fig = create_payoff_comparison_chart(comparison, currency_symbol)
        st.plotly_chart(fig, use_container_width=True)
        
        # Smart Recommendations
        st.markdown("### 💡 Personalized Guidance")
        
        st.warning("""⚠️ **Important Disclaimer:** This analysis provides general information and educational insights only. 
        It is NOT financial advice. Always consult with a qualified financial advisor who can evaluate your complete 
        financial situation, goals, and risk tolerance before making debt repayment decisions.""")
        
        st.markdown("---")
        
        best_savings = comparison.iloc[-1]
        debt_rate = debt.interest_rate * 100
        
        # Context-aware recommendations based on interest rate
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Extra Payment Impact**")
            st.metric("Fastest Payoff (Option 4)", f"{best_savings['Years_to_Payoff']} years")
            st.metric("vs Standard Payoff", f"{comparison.iloc[0]['Years_to_Payoff']} years")
            st.metric("Interest Savings", format_currency(from_base_currency(best_savings['Interest_Saved'], selected_currency), selected_currency))
        
        with col2:
            st.markdown("**🎯 Strategy Recommendation**")
            
            # High interest debt (>15%) - aggressive payoff recommended
            if debt_rate >= 15:
                st.error(f"""
                **🔴 HIGH PRIORITY DEBT ({debt_rate:.1f}%)**
                
                This high-interest debt is very costly. Consider:
                - Paying this off as aggressively as possible
                - This should typically be prioritized over investing
                - Extra payments here provide a guaranteed '{debt_rate:.1f}%' return
                - Consider balance transfer to lower rate if available
                """)
            
            # Medium interest debt (7-15%) - balance approach
            elif debt_rate >= 7:
                st.warning(f"""
                **🟡 MODERATE PRIORITY ({debt_rate:.1f}%)**
                
                This debt has a moderate interest rate. Consider:
                - Balancing extra payments with retirement contributions
                - If you have employer 401k match, prioritize that first
                - Extra payments provide a guaranteed '{debt_rate:.1f}%' return
                - Review your investment returns vs this debt cost
                """)
            
            # Low interest debt (<7%) - opportunity cost matters
            else:
                st.info(f"""
                **🟢 LOWER PRIORITY ({debt_rate:.1f}%)**
                
                This low-interest debt may not be your top priority:
                - Historical stock market returns (~7-10%) may exceed this rate
                - Consider maximizing retirement/investment contributions first
                - Emergency fund should also take priority
                - Extra payments still provide a guaranteed '{debt_rate:.1f}%' return
                
                **Tradeoff Example:**
                - Extra payment: Guaranteed {debt_rate:.1f}% 'return' (saved interest)
                - Investing: Potential 7-10% return (with market risk)
                """)
        
        st.markdown("---")
        st.caption("""💡 **Key Principle:** Pay minimums on all debts, then direct extra payments to highest-interest 
        debt first ("avalanche method"). Once high-interest debts are cleared, evaluate the tradeoff between 
        paying low-interest debt vs investing for potentially higher returns.""")
