"""
Admin Analytics Dashboard
For developers to access and analyze user data
Requires admin authentication
"""

import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from data_layer.database import SessionLocal, User, Simulation, SavedBudget, UsageStats, Feedback
from services.analytics_module import (
    export_all_analytics,
    generate_user_demographics_df,
    generate_simulation_details_df,
    generate_age_segmented_df,
    generate_income_segmented_df,
    generate_property_ownership_df,
    generate_retirement_planning_df,
    generate_savings_behavior_df,
    generate_summary_stats_df
)
from sqlalchemy import text
import pandas as pd
from datetime import datetime, timedelta

# Set page config first
st.set_page_config(page_title="Admin Analytics", page_icon="📊", layout="wide")

# Admin user list - must match wealth_simulator.py
ADMIN_USERS = ['admin', 'nbourke', 'testuser']

# Check access immediately - before rendering anything
if not st.session_state.get('authenticated', False):
    st.error("🔒 Please log in to access analytics")
    st.info("👉 Return to main app to log in")
    if st.button("← Back to Main App"):
        st.switch_page("wealth_simulator.py")
    st.stop()

if st.session_state.get('username') not in ADMIN_USERS:
    st.error("🔒 Admin access required")
    st.warning(f"Access denied for user: {st.session_state.get('username')}")
    st.info("Contact an administrator if you need access to analytics.")
    if st.button("← Back to Main App"):
        st.switch_page("wealth_simulator.py")
    st.stop()


def show_admin_analytics():
    """Display admin analytics dashboard"""
    
    st.title("📊 Admin Analytics Dashboard")
    
    # Back button at top
    if st.button("← Back to Main App", type="secondary"):
        st.switch_page("wealth_simulator.py")
    
    st.markdown("---")
    
    # Quick stats at top
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_sims = db.query(Simulation).count()
        total_budgets = db.query(SavedBudget).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_users = db.query(User).filter(User.created_at >= week_ago).count()
        recent_sims = db.query(Simulation).filter(Simulation.created_at >= week_ago).count()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Users", total_users, f"+{recent_users} this week")
        col2.metric("Total Simulations", total_sims, f"+{recent_sims} this week")
        col3.metric("Saved Budgets", total_budgets)
        col4.metric("Avg Sims/User", f"{total_sims/total_users:.1f}" if total_users > 0 else "0")
        col5.metric("Active Users", recent_users)
        
    finally:
        db.close()
    
    st.markdown("---")
    
    # Tabs for different analytics views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📥 Export Data", 
        "👥 User Analytics", 
        "💰 Financial Analytics",
        "📊 Raw Database",
        "🔍 Custom Queries",
        "💬 User Feedback"
    ])
    
    # ========== TAB 1: EXPORT DATA ==========
    with tab1:
        st.subheader("📥 Download Analytics Reports")
        st.markdown("Generate and download all analytics datasets as CSV files")
        
        if st.button("🔄 Generate Fresh Analytics", type="primary"):
            with st.spinner("Generating analytics..."):
                exports = export_all_analytics()
                st.success("✅ Analytics generated!")
                
                st.markdown("### Download Reports")
                
                col1, col2 = st.columns(2)
                
                for idx, (name, df) in enumerate(exports.items()):
                    col = col1 if idx % 2 == 0 else col2
                    
                    if len(df) > 0:
                        csv = df.to_csv(index=False)
                        col.download_button(
                            label=f"📊 {name.replace('_', ' ').title()} ({len(df)} rows)",
                            data=csv,
                            file_name=f"{name}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            key=f"download_{name}"
                        )
                    else:
                        col.info(f"No data for {name}")
    
    # ========== TAB 2: USER ANALYTICS ==========
    with tab2:
        st.subheader("👥 User Behavior Analytics")
        
        users_df = generate_user_demographics_df()
        
        if len(users_df) > 0:
            # Age distribution
            st.markdown("### Age Distribution")
            age_dist = users_df['current_age'].value_counts().sort_index()
            st.bar_chart(age_dist)
            
            # Retirement planning
            st.markdown("### Retirement Planning")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Current Age", f"{users_df['current_age'].mean():.1f}")
                st.metric("Average Retirement Age", f"{users_df['target_retirement_age'].mean():.1f}")
            
            with col2:
                st.metric("Average Years to Retirement", f"{users_df['years_to_retirement'].mean():.1f}")
                
            # Country distribution
            if 'country' in users_df.columns:
                st.markdown("### Users by Country")
                country_counts = users_df['country'].value_counts()
                st.bar_chart(country_counts)
            
            # User activity timeline
            st.markdown("### User Registration Timeline")
            if 'account_created' in users_df.columns:
                users_df['account_created'] = pd.to_datetime(users_df['account_created'])
                daily_signups = users_df.groupby(users_df['account_created'].dt.date).size()
                st.line_chart(daily_signups)
            
            # Show raw data
            with st.expander("📋 View User Demographics Table"):
                st.dataframe(users_df, use_container_width=True)
        else:
            st.info("No user data available")
    
    # ========== TAB 3: FINANCIAL ANALYTICS ==========
    with tab3:
        st.subheader("💰 Financial Behavior Analytics")
        
        sims_df = generate_simulation_details_df()
        
        if len(sims_df) > 0:
            # Savings rate distribution
            st.markdown("### Savings Rate Distribution")
            savings_bins = pd.cut(sims_df['savings_rate_pct'], 
                                bins=[-100, 0, 10, 20, 30, 40, 50, 100],
                                labels=['Deficit', '0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+'])
            st.bar_chart(savings_bins.value_counts())
            
            # Income vs Savings
            st.markdown("### Income vs Monthly Savings")
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Annual Income", f"€{sims_df['gross_annual_income'].mean():,.0f}")
            col2.metric("Avg Monthly Savings", f"€{sims_df['monthly_savings'].mean():,.0f}")
            col3.metric("Avg Savings Rate", f"{sims_df['savings_rate_pct'].mean():.1f}%")
            
            # Property ownership
            st.markdown("### Property Ownership")
            property_df = generate_property_ownership_df()
            if len(property_df) > 0:
                col1, col2 = st.columns(2)
                col1.metric("Property Owners", property_df['total_property_owners'].iloc[0])
                col2.metric("With Mortgage", f"{property_df['pct_with_mortgage'].iloc[0]:.1f}%")
                
                col1.metric("Avg Property Value", f"€{property_df['avg_property_value'].iloc[0]:,.0f}")
                col2.metric("Avg Mortgage", f"€{property_df['avg_mortgage'].iloc[0]:,.0f}")
            
            # Age-segmented analysis
            st.markdown("### Financial Metrics by Age")
            age_df = generate_age_segmented_df()
            if len(age_df) > 0:
                st.dataframe(age_df, use_container_width=True)
            
            # Currency distribution
            st.markdown("### Simulations by Currency")
            currency_counts = sims_df['currency'].value_counts()
            st.bar_chart(currency_counts)
            
            # Show raw data
            with st.expander("📋 View Simulation Details Table"):
                st.dataframe(sims_df, use_container_width=True)
        else:
            st.info("No simulation data available")
    
    # ========== TAB 4: RAW DATABASE ==========
    with tab4:
        st.subheader("📊 Raw Database Tables")
        
        db = SessionLocal()
        try:
            table_choice = st.selectbox(
                "Select Table",
                ["users", "simulations", "saved_budgets", "usage_stats"]
            )
            
            if table_choice == "users":
                users = db.query(User).all()
                data = [{
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'current_age': u.current_age,
                    'target_retirement_age': u.target_retirement_age,
                    'country': u.country,
                    'created_at': u.created_at,
                    'last_login': u.last_login
                } for u in users]
                
            elif table_choice == "simulations":
                sims = db.query(Simulation).limit(100).all()  # Limit for performance
                data = [{
                    'id': s.id,
                    'user_id': s.user_id,
                    'name': s.name,
                    'currency': s.currency,
                    'simulation_years': s.simulation_years,
                    'income_bracket': s.income_bracket,
                    'probability_of_success': s.probability_of_success,
                    'created_at': s.created_at
                } for s in sims]
                
            elif table_choice == "saved_budgets":
                budgets = db.query(SavedBudget).all()
                data = [{
                    'id': b.id,
                    'user_id': b.user_id,
                    'name': b.name,
                    'currency': b.currency,
                    'created_at': b.created_at
                } for b in budgets]
                
            elif table_choice == "usage_stats":
                stats = db.query(UsageStats).all()
                data = [{
                    'id': s.id,
                    'user_id': s.user_id,
                    'simulations_this_month': s.simulations_this_month,
                    'exports_this_month': s.exports_this_month,
                    'current_month': s.current_month
                } for s in stats]
            
            df = pd.DataFrame(data)
            
            st.markdown(f"**Total Records:** {len(df)}")
            
            # Download option
            if len(df) > 0:
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {table_choice}.csv",
                    data=csv,
                    file_name=f"{table_choice}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            st.dataframe(df, use_container_width=True)
            
        finally:
            db.close()
    
    # ========== TAB 5: CUSTOM QUERIES ==========
    with tab5:
        st.subheader("🔍 Custom SQL Queries")
        st.warning("⚠️ Advanced users only. Use SELECT queries only for safety.")
        
        # Predefined queries
        st.markdown("### Quick Queries")
        query_templates = {
            "Age and wealth correlation": """
                SELECT 
                    u.current_age,
                    s.initial_liquid_wealth_bracket,
                    COUNT(*) as count
                FROM users u
                JOIN simulations s ON u.id = s.user_id
                GROUP BY u.current_age, s.initial_liquid_wealth_bracket
                ORDER BY u.current_age;
            """,
            "Savings rate by income": """
                SELECT 
                    s.income_bracket,
                    AVG(CAST(s.parameters->>'gross_annual_income' AS NUMERIC)) as avg_income,
                    AVG(CAST(s.parameters->>'monthly_expenses' AS NUMERIC)) as avg_expenses,
                    COUNT(*) as count
                FROM simulations s
                WHERE s.parameters->>'gross_annual_income' IS NOT NULL
                GROUP BY s.income_bracket
                ORDER BY avg_income;
            """,
            "Recent user activity": """
                SELECT 
                    u.username,
                    COUNT(s.id) as simulation_count,
                    MAX(s.created_at) as last_simulation,
                    u.last_login
                FROM users u
                LEFT JOIN simulations s ON u.id = s.user_id
                GROUP BY u.id, u.username, u.last_login
                ORDER BY last_simulation DESC
                LIMIT 20;
            """,
            "Property ownership by age": """
                SELECT 
                    FLOOR(u.current_age / 5) * 5 as age_bracket,
                    COUNT(CASE WHEN s.has_property_purchase THEN 1 END) as with_property,
                    COUNT(*) as total,
                    ROUND(100.0 * COUNT(CASE WHEN s.has_property_purchase THEN 1 END) / COUNT(*), 2) as pct
                FROM users u
                JOIN simulations s ON u.id = s.user_id
                GROUP BY age_bracket
                ORDER BY age_bracket;
            """
        }
        
        selected_query = st.selectbox("Select a query template", list(query_templates.keys()))
        
        st.markdown("### Query Editor")
        custom_query = st.text_area(
            "SQL Query",
            value=query_templates[selected_query],
            height=200
        )
        
        if st.button("▶️ Run Query", type="primary"):
            # Safety check - only allow SELECT queries
            if not custom_query.strip().upper().startswith('SELECT'):
                st.error("⛔ Only SELECT queries are allowed for safety")
            else:
                db = SessionLocal()
                try:
                    result = db.execute(text(custom_query))
                    data = result.fetchall()
                    columns = result.keys()
                    
                    df = pd.DataFrame(data, columns=columns)
                    
                    st.success(f"✅ Query returned {len(df)} rows")
                    
                    if len(df) > 0:
                        # Download option
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results",
                            data=csv,
                            file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("Query returned no results")
                        
                except Exception as e:
                    st.error(f"❌ Query Error: {str(e)}")
                finally:
                    db.close()
    
    # ========== TAB 6: USER FEEDBACK ==========
    with tab6:
        st.subheader("💬 User Feedback & Issues")
        st.markdown("View and manage user feedback submissions")
        
        db = SessionLocal()
        try:
            # Filter options
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                status_filter = st.selectbox(
                    "Status",
                    ["All", "new", "reviewed", "resolved", "closed"],
                    index=0
                )
            
            with col2:
                type_filter = st.selectbox(
                    "Type",
                    ["All", "bug", "feature", "general", "issue"],
                    index=0
                )
            
            with col3:
                sort_by = st.selectbox(
                    "Sort By",
                    ["Newest First", "Oldest First", "Type"],
                    index=0
                )
            
            # Build query
            query = db.query(Feedback).join(User)
            
            if status_filter != "All":
                query = query.filter(Feedback.status == status_filter)
            
            if type_filter != "All":
                query = query.filter(Feedback.feedback_type == type_filter)
            
            # Sort
            if sort_by == "Newest First":
                query = query.order_by(Feedback.created_at.desc())
            elif sort_by == "Oldest First":
                query = query.order_by(Feedback.created_at.asc())
            else:
                query = query.order_by(Feedback.feedback_type, Feedback.created_at.desc())
            
            feedbacks = query.all()
            
            st.markdown(f"**Showing {len(feedbacks)} feedback items**")
            
            if len(feedbacks) == 0:
                st.info("No feedback submissions found")
            else:
                # Display feedback items
                for feedback in feedbacks:
                    user = db.query(User).filter(User.id == feedback.user_id).first()
                    
                    # Status emoji
                    status_emoji = {
                        'new': '🆕',
                        'reviewed': '👀',
                        'resolved': '✅',
                        'closed': '🔒'
                    }
                    
                    # Type emoji
                    type_emoji = {
                        'bug': '🐛',
                        'feature': '💡',
                        'general': '💬',
                        'issue': '⚠️'
                    }
                    
                    with st.expander(
                        f"{status_emoji.get(feedback.status, '📝')} {type_emoji.get(feedback.feedback_type, '📝')} "
                        f"{feedback.subject} - @{user.username if user else 'Unknown'} "
                        f"({feedback.created_at.strftime('%Y-%m-%d %H:%M')})"
                    ):
                        col_a, col_b = st.columns([2, 1])
                        
                        with col_a:
                            st.markdown(f"**Type:** {feedback.feedback_type.title()}")
                            st.markdown(f"**Status:** {feedback.status.title()}")
                            st.markdown(f"**User:** {user.username if user else 'Unknown'} ({feedback.user_email or 'No email'})")
                            if feedback.page_context:
                                st.markdown(f"**Context:** {feedback.page_context}")
                            st.markdown(f"**Submitted:** {feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        with col_b:
                            # Quick actions
                            new_status = st.selectbox(
                                "Update Status",
                                ["new", "reviewed", "resolved", "closed"],
                                index=["new", "reviewed", "resolved", "closed"].index(feedback.status),
                                key=f"status_{feedback.id}"
                            )
                            
                            if st.button("💾 Save Status", key=f"save_{feedback.id}"):
                                feedback.status = new_status
                                if new_status == "resolved":
                                    feedback.resolved_at = datetime.now()
                                db.commit()
                                st.success("Status updated!")
                                st.rerun()
                        
                        st.markdown("---")
                        st.markdown("**Message:**")
                        st.markdown(feedback.message)
                        
                        if feedback.admin_notes:
                            st.markdown("**Admin Notes:**")
                            st.info(feedback.admin_notes)
                        
                        # Add admin notes
                        admin_notes = st.text_area(
                            "Admin Notes",
                            value=feedback.admin_notes or "",
                            key=f"notes_{feedback.id}",
                            height=100
                        )
                        
                        if st.button("💾 Save Notes", key=f"save_notes_{feedback.id}"):
                            feedback.admin_notes = admin_notes
                            db.commit()
                            st.success("Notes saved!")
                            st.rerun()
                
                # Export option
                st.markdown("---")
                if st.button("📥 Export All Feedback to CSV"):
                    feedback_data = []
                    for feedback in feedbacks:
                        user = db.query(User).filter(User.id == feedback.user_id).first()
                        feedback_data.append({
                            'ID': feedback.id,
                            'Type': feedback.feedback_type,
                            'Status': feedback.status,
                            'Subject': feedback.subject,
                            'Message': feedback.message,
                            'Username': user.username if user else 'Unknown',
                            'Email': feedback.user_email or '',
                            'Context': feedback.page_context or '',
                            'Created': feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'Resolved': feedback.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if feedback.resolved_at else '',
                            'Admin Notes': feedback.admin_notes or ''
                        })
                    
                    feedback_df = pd.DataFrame(feedback_data)
                    csv = feedback_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Feedback CSV",
                        data=csv,
                        file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        finally:
            db.close()


# Call the main function directly (not in __main__ block for Streamlit multipage)
show_admin_analytics()
