import streamlit as st


def show_docs():
    """Display the Documentation page"""
    
    # Debug: Simple title to confirm page loads
    st.title("📚 Documentation & User Guide")
    
    st.markdown("""
<style>
.main {
padding: 2rem;
}
.hero-section {
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
padding: 3rem;
border-radius: 10px;
margin-bottom: 2rem;
text-align: center;
}
.doc-section {
background: #f8f9fa;
padding: 2rem;
border-radius: 8px;
margin-bottom: 1.5rem;
border-left: 4px solid #667eea;
}
.doc-section h2 {
color: #667eea;
margin-bottom: 1rem;
}
.tip-box {
background: #e8f5e9;
border-left: 4px solid #4caf50;
padding: 1rem;
margin: 1rem 0;
border-radius: 4px;
}
.warning-box {
background: #fff3cd;
border-left: 4px solid #ffc107;
padding: 1rem;
margin: 1rem 0;
border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

    # Hero
    st.markdown("""
<div class="hero-section">
<h1>📚 FinSim Documentation</h1>
<p style="font-size: 1.2rem;">Learn how to plan your financial future</p>
</div>
    """, unsafe_allow_html=True)

    # Quick Start
    st.markdown("""
<div class="doc-section">
<h2>🚀 Quick Start Guide</h2>
<h3>1. Create an Account</h3>
<ol>
<li>Click "Create Account" on the homepage</li>
<li>Enter your username, email, and password</li>
<li>Set your current age and target retirement age</li>
<li>Agree to terms and data sharing policy</li>
</ol>
    
<h3>2. Set Up Your Initial Position</h3>
<ul>
<li><strong>Currency:</strong> Select your preferred currency</li>
<li><strong>Age & Retirement:</strong> Your current age and when you plan to retire</li>
<li><strong>Income & Expenses:</strong> Gross annual income and monthly expenses</li>
<li><strong>Wealth:</strong> Liquid assets (savings, investments)</li>
<li><strong>Property:</strong> Real estate value and mortgage balance</li>
</ul>
    
<h3>3. Run Your First Simulation</h3>
<ol>
<li>Review your inputs in the sidebar</li>
<li>Click "Run Monte Carlo Simulation"</li>
<li>View results: median, percentiles, probability of success</li>
<li>Export to PDF or Excel if desired</li>
</ol>
</div>
    """, unsafe_allow_html=True)

    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Simulation", 
        "🏦 Pension Planner", 
        "📊 Budget Builder", 
        "🎯 Life Events",
        "📈 Understanding Results"
    ])

    with tab1:
        st.markdown("""
<div class="doc-section">
<h2>💰 Wealth Simulation</h2>
            
<h3>What is Monte Carlo Simulation?</h3>
<p>Instead of showing one possible future, FinSim runs 1,000 different scenarios with 
varying market returns, inflation, and life events. This gives you a realistic range 
of outcomes.</p>
            
<h3>Key Parameters</h3>
<ul>
<li><strong>Expected Portfolio Return:</strong> Average annual return (default: 7%)</li>
<li><strong>Return Volatility:</strong> Market fluctuation (default: 15%)</li>
<li><strong>Inflation Rate:</strong> Cost of living increase (default: 2.5%)</li>
<li><strong>Savings Rate:</strong> % of income saved monthly (default: 20%)</li>
</ul>
            
<h3>Spouse/Partner Planning</h3>
<p>Enable "Include Spouse/Partner" to model dual-income households:</p>
<ul>
<li>Each person has their own retirement age</li>
<li>Household income continues until both are retired</li>
<li>Combined pension benefits</li>
</ul>
            
<div class="tip-box">
<strong>💡 Tip:</strong> Conservative estimates (lower returns, higher expenses) give 
    more reliable projections. Markets don't always match historical averages!
</div>
</div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
<div class="doc-section">
<h2>🏦 UK Pension Planner</h2>
            
<h3>State Pension</h3>
<p>Calculate your UK State Pension based on National Insurance contributions:</p>
<ul>
<li><strong>Full Pension:</strong> £221.20/week (2024/25) requires 35 qualifying years</li>
<li><strong>Minimum:</strong> 10 years for any pension</li>
<li><strong>Forecast:</strong> Enter your expected qualifying years</li>
<li><strong>Spouse:</strong> Each person gets their own State Pension</li>
</ul>
            
<h3>USS (Universities Superannuation Scheme)</h3>
<p>For university employees:</p>
<ul>
<li><strong>Pensionable Salary:</strong> Your salary for pension calculations</li>
<li><strong>Years of Service:</strong> Expected total years in USS</li>
<li><strong>Accrual Rate:</strong> 1/75 or 1/85 of salary per year</li>
<li><strong>AVCs:</strong> Additional Voluntary Contributions</li>
<li><strong>Lump Sum:</strong> Tax-free lump sum at retirement (3x annual pension)</li>
</ul>
            
<h3>SIPP (Self-Invested Personal Pension)</h3>
<p>Private pension planning:</p>
<ul>
<li><strong>Current Value:</strong> Your existing SIPP balance</li>
<li><strong>Monthly Contributions:</strong> How much you add monthly</li>
<li><strong>Employer Match:</strong> If applicable</li>
<li><strong>Growth Rate:</strong> Expected investment return</li>
<li><strong>Withdrawal:</strong> Annual amount in retirement (4% rule suggested)</li>
</ul>
            
<div class="tip-box">
<strong>💡 Tip:</strong> Check your State Pension forecast at gov.uk/check-state-pension
</div>
</div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
<div class="doc-section">
<h2>📊 Budget Builder</h2>
            
<h3>How It Works</h3>
<p>Track your monthly expenses with Expected vs Actual budgeting:</p>
<ol>
<li><strong>Select Month:</strong> Choose current or historical month</li>
<li><strong>Set Expected Budget:</strong> Plan your spending for each category</li>
<li><strong>Enter Actual Spending:</strong> Record what you actually spent</li>
<li><strong>Review Variance:</strong> See where you over/under-spent</li>
</ol>
            
<h3>Expense Categories</h3>
<ul>
<li><strong>Housing:</strong> Rent, mortgage, property tax, insurance</li>
<li><strong>Utilities:</strong> Electric, gas, water, internet, phone</li>
<li><strong>Food:</strong> Groceries and dining out</li>
<li><strong>Transportation:</strong> Car payment, gas, insurance, public transit</li>
<li><strong>Healthcare:</strong> Insurance, prescriptions, co-pays</li>
<li><strong>Personal:</strong> Clothing, haircuts, personal care</li>
<li><strong>Entertainment:</strong> Streaming, hobbies, events</li>
<li><strong>Savings:</strong> Emergency fund, investments</li>
<li><strong>Debt:</strong> Credit cards, student loans</li>
<li><strong>Other:</strong> Everything else</li>
</ul>
            
<h3>One-Time Events</h3>
<p>Add irregular expenses:</p>
<ul>
<li>Holiday gifts</li>
<li>Car repairs</li>
<li>Medical bills</li>
<li>Travel expenses</li>
</ul>
            
<h3>Save & Load</h3>
<ul>
<li><strong>Save Budget:</strong> Store current month's budget to database</li>
<li><strong>Load Budget:</strong> Retrieve a saved budget</li>
<li><strong>Templates:</strong> Create reusable budget templates</li>
</ul>
            
<div class="tip-box">
<strong>💡 Tip:</strong> Use "New Month" to start fresh while keeping your expected 
    budget as a template. Track 3+ months to see patterns!
</div>
</div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("""
<div class="doc-section">
<h2>🎯 Life Events</h2>
            
<h3>Why Model Life Events?</h3>
<p>Major life changes have significant financial impacts. Model them to see long-term effects:</p>
            
<h3>Property Purchase</h3>
<ul>
<li><strong>Year:</strong> When you'll buy</li>
<li><strong>Price:</strong> Property value</li>
<li><strong>Down Payment:</strong> Upfront payment (reduces liquid wealth)</li>
<li><strong>Mortgage:</strong> Loan amount and terms</li>
<li><strong>Annual Appreciation:</strong> Property value growth rate</li>
</ul>
            
<h3>Property Sale</h3>
<ul>
<li><strong>Year:</strong> When you'll sell</li>
<li><strong>Sale Price:</strong> Expected value (or appreciation rate)</li>
<li><strong>Proceeds:</strong> Added to liquid wealth</li>
<li><strong>Mortgage Payoff:</strong> Outstanding balance paid from proceeds</li>
</ul>
            
<h3>Rental Income</h3>
<ul>
<li><strong>Start/End Year:</strong> Income period</li>
<li><strong>Monthly Rent:</strong> Income amount</li>
<li><strong>Expenses:</strong> Maintenance, property tax, insurance</li>
</ul>
            
<h3>Child Arrival</h3>
<ul>
<li><strong>Birth Year:</strong> When child is born</li>
<li><strong>Monthly Cost:</strong> Childcare, food, clothing ($500-2000/month typical)</li>
<li><strong>Duration:</strong> Usually modeled until age 18</li>
<li><strong>Education Fund:</strong> Optional university savings</li>
</ul>
            
<h3>Career Change</h3>
<ul>
<li><strong>Year:</strong> When change occurs</li>
<li><strong>New Income:</strong> Salary increase or decrease</li>
<li><strong>One-time Costs:</strong> Moving, training, etc.</li>
</ul>
            
<h3>International Move</h3>
<ul>
<li><strong>Year:</strong> When you relocate</li>
<li><strong>New Currency:</strong> Automatically converted</li>
<li><strong>Moving Costs:</strong> Shipping, flights, deposits</li>
<li><strong>Income Adjustment:</strong> New salary in new currency</li>
</ul>
            
<h3>Major Expense</h3>
<ul>
<li><strong>Year:</strong> When expense occurs</li>
<li><strong>Amount:</strong> One-time cost</li>
<li><strong>Examples:</strong> Wedding, car purchase, home renovation</li>
</ul>
            
<div class="warning-box">
<strong>⚠️ Note:</strong> Life events are simplified models. Real life is more complex. 
    Use these as approximations, not exact predictions.
</div>
</div>
        """, unsafe_allow_html=True)

    with tab5:
        st.markdown("""
<div class="doc-section">
<h2>📈 Understanding Your Results</h2>
            
<h3>Main Chart: Net Worth Over Time</h3>
<p>Shows your projected net worth from now until target year:</p>
<ul>
<li><strong>Median (50th percentile):</strong> Middle outcome - half better, half worse</li>
<li><strong>10th percentile:</strong> Pessimistic scenario (only 10% worse than this)</li>
<li><strong>90th percentile:</strong> Optimistic scenario (only 10% better than this)</li>
<li><strong>Shaded area:</strong> Range of likely outcomes</li>
</ul>
            
<h3>Key Metrics</h3>
<ul>
<li><strong>Median Final Net Worth:</strong> Most likely outcome</li>
<li><strong>Probability of Growth:</strong> Chance your wealth increases</li>
<li><strong>Probability of 2x Growth:</strong> Chance you double your wealth</li>
<li><strong>Retirement Readiness:</strong> Can you afford to retire?</li>
</ul>
            
<h3>Wealth Composition Chart</h3>
<p>Breakdown of your net worth over time:</p>
<ul>
<li><strong>Liquid Wealth:</strong> Savings and investments (green)</li>
<li><strong>Property Value:</strong> Real estate equity (blue)</li>
<li><strong>Mortgage Debt:</strong> Outstanding loan balance (red)</li>
</ul>
            
<h3>Cash Flow Projection</h3>
<p>Year-by-year income and expenses:</p>
<ul>
<li><strong>Income:</strong> Salary, rental income, pension</li>
<li><strong>Expenses:</strong> Living costs, mortgage, children</li>
<li><strong>Net Savings:</strong> Income - Expenses</li>
<li><strong>Accumulated Wealth:</strong> Running total</li>
</ul>
            
<h3>How to Interpret Results</h3>
            
<h4>✅ Good Signs:</h4>
<ul>
<li>10th percentile stays above £0 (low bankruptcy risk)</li>
<li>Median net worth grows over time</li>
<li>High probability of growth (>80%)</li>
<li>Retirement readiness >70%</li>
</ul>
            
<h4>⚠️ Warning Signs:</h4>
<ul>
<li>10th percentile goes negative (bankruptcy risk)</li>
<li>Declining net worth in median scenario</li>
<li>Low probability of growth (<50%)</li>
<li>Retirement readiness <50%</li>
</ul>
            
<h3>What to Do With Results</h3>
            
<h4>If results look good:</h4>
<ul>
<li>✅ Continue your current strategy</li>
<li>✅ Consider more aggressive savings for earlier retirement</li>
<li>✅ Model new life events (property, children)</li>
</ul>
            
<h4>If results look concerning:</h4>
<ul>
<li>💡 Increase savings rate</li>
<li>💡 Reduce expenses</li>
<li>💡 Delay retirement age</li>
<li>💡 Consider additional income sources</li>
<li>💡 Adjust portfolio allocation (higher returns, more risk)</li>
</ul>
            
<div class="warning-box">
<strong>⚠️ Remember:</strong> These are projections, not predictions. Markets fluctuate, 
    life happens, and no model is perfect. Use FinSim as ONE tool in your planning toolkit, 
    and always consult with qualified financial advisors for major decisions.
</div>
</div>
        """, unsafe_allow_html=True)

    # Best Practices
    st.markdown("""
<div class="doc-section">
<h2>✨ Best Practices</h2>
        
<h3>1. Be Conservative</h3>
<ul>
<li>Use lower return estimates than historical averages</li>
<li>Overestimate expenses slightly</li>
<li>Add buffer for unexpected costs</li>
</ul>
        
<h3>2. Update Regularly</h3>
<ul>
<li>Re-run simulations quarterly or annually</li>
<li>Update with actual income/expense changes</li>
<li>Adjust as life events occur</li>
</ul>
        
<h3>3. Model Multiple Scenarios</h3>
<ul>
<li>Baseline: Current plan</li>
<li>Optimistic: Higher income, lower expenses</li>
<li>Pessimistic: Job loss, market crash</li>
</ul>
        
<h3>4. Export and Compare</h3>
<ul>
<li>Download PDF reports for each scenario</li>
<li>Compare results side-by-side</li>
<li>Track changes over time</li>
</ul>
        
<h3>5. Don't Rely on FinSim Alone</h3>
<ul>
<li>Consult professional financial advisors</li>
<li>Consider tax implications (not modeled in FinSim)</li>
<li>Account for company benefits, inheritance, etc.</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Limitations
    st.markdown("""
<div class="doc-section">
<h2>⚠️ Limitations & Assumptions</h2>
        
<h3>What FinSim DOES NOT Account For:</h3>
<ul>
<li>❌ Taxes (income, capital gains, property)</li>
<li>❌ Company pension matching (beyond what you enter)</li>
<li>❌ Healthcare costs in retirement</li>
<li>❌ Inheritance or windfalls</li>
<li>❌ Divorce, legal issues</li>
<li>❌ Market crashes (modeled as volatility, but not specific events)</li>
<li>❌ Inflation variations (uses constant rate)</li>
<li>❌ Currency exchange rate fluctuations</li>
</ul>
        
<h3>Key Assumptions:</h3>
<ul>
<li>Returns follow a normal distribution (real markets don't always)</li>
<li>You can consistently achieve the savings rate</li>
<li>Expenses remain constant (adjusted for inflation)</li>
<li>Property appreciates at steady rate</li>
<li>No major health or disability issues</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    
    # Back to home button
    if st.button("← Back to Home", key="docs_back", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer links as buttons
    footer_col1, footer_col2 = st.columns(2)
    with footer_col1:
        if st.button("About", key="docs_to_about", use_container_width=True):
            st.query_params['page'] = 'about'
            st.rerun()
    with footer_col2:
        if st.button("Contact Support", key="docs_to_contact", use_container_width=True):
            st.query_params['page'] = 'contact'
            st.rerun()
