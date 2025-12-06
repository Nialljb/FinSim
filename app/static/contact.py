import streamlit as st
from datetime import datetime
from data_layer.database import submit_contact_form


def show_contact():
    """Display the Contact page"""
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
    .contact-box {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #667eea;
    }
    .contact-box h3 {
        color: #667eea;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="hero-section">
        <h1>📧 Contact Us</h1>
        <p style="font-size: 1.2rem;">We'd love to hear from you!</p>
    </div>
    """, unsafe_allow_html=True)

    # # Contact Methods
    # col1, col2 = st.columns(2)

    # with col1:
    #     st.markdown("""
    #     <div class="contact-box">
    #         <h3>📧 Email</h3>
    #         <p><strong>General Inquiries:</strong><br>
    #         info@finsim.com (placeholder)</p>
            
    #         <p><strong>Support:</strong><br>
    #         support@finsim.com (placeholder)</p>
            
    #         <p><strong>Privacy & Data:</strong><br>
    #         privacy@finsim.com (placeholder)</p>
            
    #         <p><strong>Legal:</strong><br>
    #         legal@finsim.com (placeholder)</p>
            
    #         <p style="font-size: 0.9rem; color: #666; margin-top: 1rem;">
    #         <em>We typically respond within 24-48 hours</em>
    #         </p>
    #     </div>
    #     """, unsafe_allow_html=True)

    # with col2:
    #     st.markdown("""
    #     <div class="contact-box">
    #         <h3>🐛 Report a Bug</h3>
    #         <p>Found a bug or error? Please provide:</p>
    #         <ul>
    #             <li>Steps to reproduce</li>
    #             <li>Expected vs actual behavior</li>
    #             <li>Browser and device info</li>
    #             <li>Screenshots (if applicable)</li>
    #         </ul>
    #         <p><strong>Email:</strong> bugs@finsim.com (placeholder)</p>
    #     </div>
        
    #     <div class="contact-box">
    #         <h3>💡 Feature Requests</h3>
    #         <p>Have an idea for a new feature?</p>
    #         <p><strong>Email:</strong> features@finsim.com (placeholder)</p>
    #     </div>
    # """, unsafe_allow_html=True)

    # Contact Form
    st.markdown("### ✉️ Send us a Message")

    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name*", placeholder="Your name")
            email = st.text_input("Email*", placeholder="your.email@example.com")
        
        with col2:
            subject = st.selectbox(
                "Subject*",
                [
                    "General Inquiry",
                    "Technical Support",
                    "Bug Report",
                    "Feature Request",
                    "Account Issue",
                    "Data/Privacy Question",
                    "Partnership Inquiry",
                    "Other"
                ]
            )
            
            # Add a user ID field for logged-in users
            if st.session_state.get('authenticated', False):
                st.info(f"Logged in as: {st.session_state.get('username', 'Unknown')}")
        
        message = st.text_area(
            "Message*",
            placeholder="Tell us what's on your mind...",
            height=200
        )
        
        # Optional: Include system info for bug reports
        include_system_info = st.checkbox(
            "Include system information (helpful for bug reports)",
            value=False
        )
        
        submitted = st.form_submit_button("📤 Send Message", type="primary", use_container_width=True)
        
        if submitted:
            if not name or not email or not message:
                st.error("⚠️ Please fill in all required fields (marked with *)")
            elif "@" not in email or "." not in email:
                st.error("⚠️ Please enter a valid email address")
            else:
                # Get user ID if logged in
                user_id = st.session_state.get('user_id', None)
                
                # Submit to feedback system
                success, result_message = submit_contact_form(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                    user_id=user_id,
                    include_system_info=include_system_info
                )
                
                if success:
                    st.success(f"✅ {result_message} We'll get back to you soon.")
                    st.balloons()
                else:
                    st.error(f"❌ {result_message}")

    # FAQ Section
    st.markdown("---")
    st.markdown("### ❓ Frequently Asked Questions")

    faq_col1, faq_col2 = st.columns(2)

    with faq_col1:
        with st.expander("💰 Is FinSim really free?"):
            st.write("""
            Yes! FinSim is completely free for personal use with rate limits (10 simulations/month). 
            There are no hidden fees, ads, or premium tiers currently.
            """)
        
        with st.expander("🔒 Is my financial data secure?"):
            st.write("""
            Yes. We use industry-standard encryption (HTTPS/TLS), password hashing, and secure 
            database storage. See our [Privacy Policy](/Privacy) for details.
            """)
        
        with st.expander("📊 Can I export my data?"):
            st.write("""
            Absolutely! You can export your simulation results to PDF and Excel formats at any time.
            """)
        
        with st.expander("🗑️ How do I delete my account?"):
            st.write("""
            Email us at privacy@finsim.com (placeholder) with your username and we'll permanently 
            delete your account and data within 30 days.
            """)

    with faq_col2:
        with st.expander("🌍 What currencies are supported?"):
            st.write("""
            FinSim supports 15+ currencies including USD, CAD, EUR, GBP, JPY, AUD, NZD, CHF, SEK, 
            NOK, DKK, PLN, CZK, HUF, and ZAR.
            """)
        
        with st.expander("📱 Is there a mobile app?"):
            st.write("""
            FinSim is a web app that works on mobile browsers. There's no dedicated mobile app yet, 
            but the website is mobile-responsive.
            """)
        
        with st.expander("🔢 What's Monte Carlo simulation?"):
            st.write("""
            Monte Carlo simulation runs thousands of scenarios with varying market returns to show 
            the range of possible financial outcomes, not just one optimistic projection.
            """)
        
        with st.expander("💼 Can I use FinSim for business?"):
            st.write("""
            FinSim is designed for personal financial planning. Commercial use requires permission. 
            Contact us at info@finsim.com (placeholder) for licensing inquiries.
            """)

    # Social Links (Placeholder)
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h3>🌐 Connect With Us</h3>
        <p>
            <a href="https://github.com/Nialljb?tab=repositories" style="color: #667eea; text-decoration: none; margin: 0 1rem;">GitHub</a> • 
            <a href="https://www.linkedin.com/in/niall-bourke-phd-53003640/" style="color: #667eea; text-decoration: none; margin: 0 1rem;">LinkedIn</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # <a href="#" style="color: #667eea; text-decoration: none; margin: 0 1rem;">Twitter</a> • 
    # <p style="font-size: 0.9rem; color: #666;">
    #     <em>(Social links placeholder - update with real profiles)</em>
    # </p>

    # Footer
    st.markdown("---")
    
    # Back to home button
    if st.button("← Back to Home", key="contact_back", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer links as buttons
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    with footer_col1:
        if st.button("About", key="contact_to_about", use_container_width=True):
            st.query_params['page'] = 'about'
            st.rerun()
    with footer_col2:
        if st.button("Privacy Policy", key="contact_to_privacy", use_container_width=True):
            st.query_params['page'] = 'privacy'
            st.rerun()
    with footer_col3:
        if st.button("Terms of Service", key="contact_to_terms", use_container_width=True):
            st.query_params['page'] = 'terms'
            st.rerun()
