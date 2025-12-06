"""
UI/UX enhancements for FinSim
Improves professionalism and user experience
"""

import streamlit as st


def inject_custom_css():
    """Inject custom CSS for better styling and animations"""
    st.markdown("""
    <style>
    /* Professional styling improvements */
    
    /* Smooth transitions */
    .stButton button {
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Better tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    /* Professional input styling */
    .stNumberInput input {
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-top-color: #FF5E5B !important;
    }
    
    /* Better metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Success/Error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        padding: 1rem;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    /* Sidebar improvements */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Hide Streamlit branding in footer */
    footer {
        visibility: hidden;
    }
    
    footer:after {
        content: 'FinSim v1.0 | Built with ❤️ for Financial Planning';
        visibility: visible;
        display: block;
        text-align: center;
        padding: 1rem;
        color: #888;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        border-bottom: 1px dotted #888;
    }
    
    /* Professional data tables */
    .dataframe {
        font-size: 0.95rem;
    }
    
    /* Better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    /* Professional cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Highlight important values */
    .highlight-value {
        background: linear-gradient(120deg, #FFE66D 0%, #FFE66D 100%);
        background-repeat: no-repeat;
        background-size: 100% 40%;
        background-position: 0 90%;
        padding: 0 4px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


def add_meta_tags():
    """Add SEO and social sharing meta tags"""
    st.markdown("""
    <meta name="description" content="FinSim - Free Monte Carlo wealth simulator for financial planning. Visualize your financial future with advanced simulations, multi-currency support, and privacy-first design.">
    <meta name="keywords" content="financial planning, monte carlo simulation, retirement planning, FIRE, wealth simulator, budget planning">
    <meta name="author" content="Niall Bourke">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="FinSim - Monte Carlo Wealth Simulator">
    <meta property="og:description" content="Visualize your financial future with powerful Monte Carlo simulations. Free, privacy-first, and supports 15+ currencies.">
    <meta property="og:image" content="https://finsim.app/og-image.png">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="FinSim - Monte Carlo Wealth Simulator">
    <meta name="twitter:description" content="Visualize your financial future with powerful Monte Carlo simulations.">
    
    <!-- PWA Support -->
    <meta name="theme-color" content="#FF5E5B">
    <meta name="mobile-web-app-capable" content="yes">
    """, unsafe_allow_html=True)


def show_tooltip(text: str, tooltip: str):
    """
    Display text with tooltip on hover
    
    Args:
        text: Main text to display
        tooltip: Tooltip text on hover
    """
    st.markdown(f"""
    <span class="tooltip" title="{tooltip}">{text}</span>
    """, unsafe_allow_html=True)


def show_info_card(title: str, content: str, icon: str = "ℹ️"):
    """
    Display a professional info card
    
    Args:
        title: Card title
        content: Card content
        icon: Emoji icon
    """
    st.markdown(f"""
    <div class="info-card">
        <h3>{icon} {title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def show_keyboard_shortcuts():
    """Display keyboard shortcuts help"""
    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        - **Ctrl/Cmd + R**: Refresh simulation
        - **Ctrl/Cmd + S**: Save current simulation
        - **Ctrl/Cmd + L**: Load simulation
        - **Esc**: Close current modal
        - **Tab**: Navigate between inputs
        """)


def show_feature_highlight(feature: str, description: str, is_new: bool = False):
    """
    Highlight a feature with optional "NEW" badge
    
    Args:
        feature: Feature name
        description: Feature description
        is_new: Show "NEW" badge if True
    """
    badge = "🆕 " if is_new else ""
    st.markdown(f"""
    <div style="padding: 0.5rem 1rem; background: #f0f7ff; border-left: 4px solid #FF5E5B; margin: 0.5rem 0;">
        <strong>{badge}{feature}</strong><br>
        <span style="color: #666;">{description}</span>
    </div>
    """, unsafe_allow_html=True)


def show_loading_state(message: str = "Processing..."):
    """
    Show a professional loading state
    
    Args:
        message: Loading message to display
    """
    return st.spinner(f"🔄 {message}")


def validate_input(value, min_val=None, max_val=None, field_name="Value"):
    """
    Validate user input and show friendly error messages
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        field_name: Name of field for error message
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if value is None:
        return False, f"❌ {field_name} is required"
    
    if min_val is not None and value < min_val:
        return False, f"❌ {field_name} must be at least {min_val:,.0f}"
    
    if max_val is not None and value > max_val:
        return False, f"❌ {field_name} cannot exceed {max_val:,.0f}"
    
    return True, ""


def show_confirmation_dialog(message: str, key: str) -> bool:
    """
    Show a confirmation dialog before destructive actions
    
    Args:
        message: Confirmation message
        key: Unique key for the dialog
    
    Returns:
        True if user confirmed, False otherwise
    """
    col1, col2 = st.columns([3, 1])
    with col1:
        st.warning(message)
    with col2:
        if st.button("Confirm", key=f"{key}_confirm", type="primary"):
            return True
        if st.button("Cancel", key=f"{key}_cancel"):
            return False
    return False


def show_welcome_tour():
    """Show a welcome tour for first-time users"""
    if 'seen_tour' not in st.session_state:
        st.session_state.seen_tour = False
    
    if not st.session_state.seen_tour:
        with st.expander("👋 Welcome to FinSim! (Click to view tour)", expanded=True):
            st.markdown("""
            ### Quick Start Guide
            
            1. **Select Your Currency** - Choose from 15+ supported currencies
            2. **Enter Your Financial Position** - Current wealth, property, income
            3. **Add Life Events** - Plan for purchases, expenses, windfalls
            4. **Run Simulation** - See 100-5000 possible futures
            5. **Analyze Results** - Understand your financial trajectory
            
            💡 **Tip**: Your data is private and never leaves your session!
            """)
            
            if st.button("Got it! Don't show again"):
                st.session_state.seen_tour = True
                st.rerun()


def show_pro_tip(tip: str):
    """Display a professional tip box"""
    st.info(f"💡 **Pro Tip**: {tip}")


def show_beta_badge():
    """Show beta feature badge"""
    st.markdown("""
    <span style="background: #FF5E5B; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">
        BETA
    </span>
    """, unsafe_allow_html=True)


def create_metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """
    Create a professional metric card
    
    Args:
        label: Metric label
        value: Metric value
        delta: Change indicator (optional)
        delta_color: Color for delta ("normal", "inverse", "off")
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
