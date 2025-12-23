import streamlit as st


def show_privacy():
    """Display the Privacy Policy page"""
    st.markdown("""
<style>
.main {
padding: 2rem;
max-width: 900px;
margin: 0 auto;
}
.hero-section {
background: linear-gradient(135deg, #2B3447 0%, #667eea 100%);
color: white;
padding: 2rem;
border-radius: 10px;
margin-bottom: 2rem;
text-align: center;
}
.section {
margin-bottom: 2rem;
}
.section h2 {
color: #667eea;
margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

    # Hero
    st.markdown("""
<div class="hero-section">
<h1>🔒 Privacy Policy</h1>
<p>Last Updated: December 4, 2025</p>
</div>
    """, unsafe_allow_html=True)

    # Introduction
    st.markdown("""
<div class="section">
<h2>1. Introduction</h2>
<p>Welcome to FinSim. We take your privacy seriously. This Privacy Policy explains how we collect, 
use, and protect your personal and financial information.</p>
<p><strong>Key Principles:</strong></p>
<ul>
<li>We collect only what's necessary to provide the service</li>
<li>Your financial data never leaves our secure database</li>
<li>We don't sell or share your personal information</li>
<li>You control your data and can delete it anytime</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Information We Collect
    st.markdown("""
<div class="section">
<h2>2. Information We Collect</h2>

<h3>2.1 Account Information</h3>
<ul>
<li><strong>Username</strong> (for login)</li>
<li><strong>Email address</strong> (for account recovery and updates)</li>
<li><strong>Password</strong> (encrypted and hashed - we cannot see your password)</li>
<li><strong>Age and retirement age</strong> (for planning calculations)</li>
<li><strong>Country</strong> (optional, for regional defaults)</li>
</ul>

<h3>2.2 Financial Planning Data</h3>
<ul>
<li>Current wealth, income, and expenses</li>
<li>Property values and mortgages</li>
<li>Planned life events (children, career changes, etc.)</li>
<li>Budget and spending categories</li>
<li>Pension and retirement information</li>
<li>Spouse/partner financial information (if added)</li>
</ul>

<h3>2.3 Usage Data</h3>
<ul>
<li>Number of simulations run</li>
<li>Features used</li>
<li>Export counts (PDF/Excel)</li>
<li>Login timestamps</li>
</ul>

<h3>2.4 Technical Data</h3>
<ul>
<li>IP address (for security)</li>
<li>Browser type and version</li>
<li>Device information</li>
<li>Usage Data (Collected via server logs and essential session cookies)</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # How We Use Your Information
    st.markdown("""
<div class="section">
<h2>3. How We Use Your Information</h2>
        
<h3>3.1 To Provide the Service</h3>
<ul>
<li>Run financial simulations and projections</li>
<li>Generate reports and exports</li>
<li>Store your data for future sessions</li>
<li>Manage your account</li>
</ul>
        
<h3>3.2 To Improve FinSim</h3>
<ul>
<li>Analyze usage patterns (aggregated and/or anonymized, for legitimate business interests)</li>
<li>Identify bugs and performance issues</li>
<li>Develop new features</li>
<li>Optimize user experience</li>
</ul>
        
<h3>3.3 For Research (With Consent)</h3>
<p>If you opted in during registration, we may use <strong>anonymized, aggregated data</strong> for:</p>
<ul>
<li>Academic research on financial behavior</li>
<li>Public reporting on financial planning trends</li>
<li>Improving financial modeling algorithms</li>
</ul>
<p><em>Anonymized means: No names, emails, or identifying information. Only statistical patterns.</em></p>
        
<h3>3.4 Security & Compliance</h3>
<ul>
<li>Prevent fraud and abuse</li>
<li>Enforce rate limits</li>
<li>Comply with legal obligations</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Data Storage & Security
    st.markdown("""
<div class="section">
<h2>4. Data Storage & Security</h2>
        
<h3>4.1 Where We Store Data</h3>
<ul>
<li><strong>Database:</strong> PostgreSQL hosted on Render.com (US/EU regions)</li>
<li><strong>Application:</strong> Render.com cloud infrastructure</li>
<li><strong>Backups:</strong> Automated daily backups (7-day retention)</li>
<li>The data controller for FinSim is Metacognition.ltd, located in London,England.</li>
</ul>
        
<h3>4.2 Security Measures</h3>
<ul>
<li>✅ <strong>Encrypted connections (HTTPS/TLS)</strong> for all data transmission</li>
<li>✅ <strong>Password hashing (bcrypt)</strong> - we never store plain text passwords</li>
<li>✅ <strong>Database encryption at rest</strong></li>
<li>✅ <strong>Regular security updates</strong></li>
<li>✅ <strong>Rate limiting</strong> to prevent abuse</li>
<li>✅ <strong>Session management</strong> with automatic timeouts</li>
</ul>
        
<h3>4.3 Data Retention</h3>
<ul>
<li><strong>Active accounts:</strong> Data retained indefinitely while account is active</li>
<li><strong>Inactive accounts:</strong> After 2 years of inactivity, we may delete data</li>
<li><strong>Deleted accounts:</strong> Permanent deletion within 30 days</li>
<li><strong>Backups:</strong> Deleted from backups after 30 days</li>
<li><strong>Research data:</strong> Anonymized data retained indefinitely for research purposes</li>
<li><strong>We may retain data for longer periods if required by law (e.g., tax or legal records) or to resolve disputes.</strong></li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Data Sharing
    st.markdown("""
<div class="section">
<h2>5. Data Sharing & Disclosure</h2>
        
<h3>We DO NOT sell your data. Period.</h3>
        
<h3>5.1 We DO share data with:</h3>
<ul>
<li><strong>Service Providers:</strong> Render.com (hosting), database services and other sub-processors who assist us in operating the Service (all are required to maintain strict confidentiality and data protection standards).</li>
<li><strong>Legal Authorities:</strong> If required by law or subpoena</li>
</ul>
        
<h3>5.2 We DO NOT share with:</h3>
<ul>
<li>❌ Advertisers</li>
<li>❌ Data brokers</li>
<li>❌ Marketing companies</li>
<li>❌ Third-party analytics (no Google Analytics, no tracking pixels)</li>
</ul>
        
<h3>5.3 Anonymized Research Data</h3>
<p>If you consented, we may publish <strong>anonymized, aggregated statistics</strong> like:</p>
<ul>
<li>"Average retirement age in our dataset: 65"</li>
<li>"Median savings rate: 15%"</li>
</ul>
<p><em>This data cannot be traced back to you.</em></p>
</div>
    """, unsafe_allow_html=True)

    # Your Rights
    st.markdown("""
<div class="section">
<h2>6. Your Rights & Control</h2>
        
<h3>6.1 Your Rights</h3>
<ul>
<li>✅ <strong>Access:</strong> View all your data anytime</li>
<li>✅ <strong>Export:</strong> Download your data in PDF/Excel format</li>
<li>✅ <strong>Edit:</strong> Update or correct your information</li>
<li>✅ <strong>Delete:</strong> Permanently delete your account and data</li>
<li>✅ <strong>Withdraw Consent:</strong> Opt out of research data sharing</li>
<li>✅ <strong>Data Portability:</strong> Export in standard formats</li>
</ul>
        
<h3>6.2 How to Exercise Your Rights</h3>
<ul>
<li><strong>View/Edit Data:</strong> Use the app interface</li>
<li><strong>Export Data:</strong> Use the PDF/Excel export buttons</li>
<li><strong>Delete Account:</strong> Contact us (see Contact page)</li>
<li><strong>Questions:</strong> Email niall@finsim.com (placeholder)</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Cookies
    st.markdown("""
<div class="section">
<h2>7. Cookies & Tracking</h2>
        
<h3>7.1 Session Cookies (Essential)</h3>
<ul>
<li>Used to keep you logged in</li>
<li>Store temporary session data</li>
<li>Expire when you close the browser or logout</li>
</ul>
        
<h3>7.2 What We DON'T Use</h3>
<ul>
<li>❌ Third-party cookies</li>
<li>❌ Advertising cookies</li>
<li>❌ Cross-site tracking</li>
<li>❌ Analytics cookies (no Google Analytics)</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Children's Privacy
    st.markdown("""
<div class="section">
<h2>8. Children's Privacy</h2>
<p>FinSim is not intended for users under 18 years old. We do not knowingly collect 
information from children. If you are a parent and believe your child has created an 
account, please contact us to have it deleted.</p>
</div>
    """, unsafe_allow_html=True)

    # International Users
    st.markdown("""
<div class="section">
<h2>9. International Users</h2>
<p>FinSim is hosted in [US/EU - update based on your Render region]. If you access FinSim 
from outside this region, your data may be transferred to and stored in [US/EU].</p>
<p><strong>GDPR Compliance (EU Users):</strong></p>
<ul>
<li>You have the right to access, rectify, or delete your data</li>
<li>You can withdraw consent for data processing</li>
<li>You can lodge a complaint with your data protection authority</li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Changes to Policy
    st.markdown("""
<div class="section">
<h2>10. Changes to This Policy</h2>
<p>We may update this Privacy Policy from time to time. Changes will be posted on this page 
with an updated "Last Updated" date. Major changes will be communicated via:</p>
<ul>
<li>Email notification (if you provided an email)</li>
<li>In-app notification on login</li>
</ul>
<p>Continued use of FinSim after changes constitutes acceptance of the new policy.</p>
</div>
    """, unsafe_allow_html=True)

    # Contact
    st.markdown("""
<div class="section">
<h2>11. Contact Us</h2>
<p>Questions about this Privacy Policy or your data?</p>
<ul>
<li><strong>Email:</strong> niall@finsim.com (placeholder - update with real contact)</li>
<li><strong>Contact Form:</strong> <a href="?page=contact">Contact Page</a></li>
</ul>
</div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    
    # Back to home button
    if st.button("← Back to Home", key="privacy_back", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer links as buttons
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    with footer_col1:
        if st.button("About", key="privacy_to_about", use_container_width=True):
            st.query_params['page'] = 'about'
            st.rerun()
    with footer_col2:
        if st.button("Terms of Service", key="privacy_to_terms", use_container_width=True):
            st.query_params['page'] = 'terms'
            st.rerun()
    with footer_col3:
        if st.button("Contact", key="privacy_to_contact", use_container_width=True):
            st.query_params['page'] = 'contact'
            st.rerun()
