"""
Simple Ko-fi Integration Example
Add this to show a "Buy Me a Coffee" style donation button
"""

import streamlit as st

def show_kofi_button():
    """Display Ko-fi donation button in sidebar or main area"""
    
    st.markdown("""
        <style>
        .kofi-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #ff5e5b;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
            transition: background-color 0.3s;
        }
        .kofi-button:hover {
            background-color: #ff4542;
        }
        </style>
        
        <a href="https://ko-fi.com/nialljb" target="_blank" class="kofi-button">
            ☕ Buy Me a Coffee
        </a>
    """, unsafe_allow_html=True)


def show_support_section():
    """Display support options in sidebar"""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💝 Support FinSim")
    
    st.sidebar.markdown("""
        Enjoying FinSim? Help keep it free and ad-free!
        
        Your support helps us:
        - Keep servers running
        - Add new features
        - Provide free access to everyone
    """)
    
    # Ko-fi button
    st.sidebar.markdown("""
        <a href="https://ko-fi.com/YOUR_USERNAME" target="_blank">
            <img src="https://ko-fi.com/img/githubbutton_sm.svg" 
                 alt="Support on Ko-fi" 
                 style="height: 36px;">
        </a>
    """, unsafe_allow_html=True)
    
    # Or GitHub Sponsors
    st.sidebar.markdown("""
        <a href="https://github.com/sponsors/YOUR_USERNAME" target="_blank">
            <img src="https://img.shields.io/badge/Sponsor-GitHub-ea4aaa?logo=github" 
                 alt="Sponsor on GitHub">
        </a>
    """, unsafe_allow_html=True)


# Usage in wealth_simulator.py:
# Add to sidebar, near the bottom:
"""
if st.session_state.get('authenticated', False):
    show_support_section()
"""

# Or add to main content after simulation results:
"""
if st.session_state.get('sim_complete', False):
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Enjoying FinSim?")
        st.markdown("If this tool has been helpful, consider supporting its development!")
        show_kofi_button()
"""
