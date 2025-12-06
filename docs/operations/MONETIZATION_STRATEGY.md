# FinSim Monetization Strategy & Payment Integration

## 💰 Payment Integration Options

### 1. "Buy Me a Coffee" Style (Simplest - Recommended to Start)

**Best for:** Initial launch, building goodwill, testing demand

**Options:**
- **Ko-fi** (https://ko-fi.com)
  - No monthly fees, 0% platform fee
  - Accepts PayPal, Stripe
  - One-time donations or memberships
  - Easy widget integration
  
- **Buy Me a Coffee** (https://buymeacoffee.com)
  - 5% platform fee
  - Simple setup, clean UI
  - Supports one-time and recurring payments
  
- **GitHub Sponsors** (https://github.com/sponsors)
  - 0% fees (GitHub covers processing)
  - Good for open-source projects
  - Monthly tiers
  - Requires GitHub account

**Implementation:**
```python
# Add to user header or sidebar
st.markdown("""
    <a href="https://ko-fi.com/yourname" target="_blank">
        <img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Buy Me a Coffee">
    </a>
""", unsafe_allow_html=True)
```

**Pros:**
- ✅ No code changes needed
- ✅ Zero/minimal fees
- ✅ Users control amount
- ✅ No ongoing maintenance

**Cons:**
- ❌ No automatic feature unlocking
- ❌ Manual tracking required
- ❌ Lower revenue predictability


### 2. Stripe Integration (Recommended for Growth)

**Best for:** Automated subscriptions, one-time purchases, professional setup

**Features:**
- Payment processing (cards, wallets, bank transfers)
- Subscription management
- Webhook notifications for automation
- Customer portal for users
- International support (135+ currencies)

**Costs:**
- 2.9% + $0.30 per transaction (US)
- No monthly fees for standard plan

**Implementation Requirements:**

#### A. Database Schema Changes
```python
# Add to User model in database.py
class User(Base):
    # ... existing fields ...
    
    # Subscription fields
    subscription_tier = Column(String(50), default='free')  # 'free', 'basic', 'pro', 'lifetime'
    subscription_status = Column(String(50), default='active')  # 'active', 'canceled', 'past_due'
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    subscription_start_date = Column(DateTime(timezone=True), nullable=True)
    subscription_end_date = Column(DateTime(timezone=True), nullable=True)
    simulation_quota = Column(Integer, default=10)  # Monthly quota
    
class Transaction(Base):
    """Payment transaction history"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Stripe details
    stripe_payment_intent_id = Column(String(255), unique=True)
    stripe_invoice_id = Column(String(255), nullable=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    transaction_type = Column(String(50))  # 'subscription', 'one_time', 'simulation_pack'
    description = Column(Text)
    
    # Status
    status = Column(String(50))  # 'pending', 'completed', 'failed', 'refunded'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
```

#### B. Environment Variables
```bash
# Add to .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

#### C. Dependencies
```bash
pip install stripe
```

#### D. Payment Integration Module
```python
# Create: payment_integration.py
import stripe
import os
from database import SessionLocal, User, Transaction
from datetime import datetime, timedelta

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_checkout_session(user_id: int, price_id: str, success_url: str, cancel_url: str):
    """Create Stripe checkout session for subscription or one-time payment"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        # Create or get Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'user_id': user_id}
            )
            user.stripe_customer_id = customer.id
            db.commit()
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',  # or 'payment' for one-time
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'user_id': user_id}
        )
        
        return session.url
        
    finally:
        db.close()

def handle_webhook(payload, sig_header):
    """Handle Stripe webhook events"""
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            fulfill_order(session)
            
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            renew_subscription(invoice)
            
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            cancel_subscription(subscription)
            
        return True
    except Exception as e:
        print(f"Webhook error: {e}")
        return False

def fulfill_order(session):
    """Grant access after successful payment"""
    db = SessionLocal()
    try:
        user_id = int(session['metadata']['user_id'])
        user = db.query(User).filter(User.id == user_id).first()
        
        # Update user subscription
        subscription = stripe.Subscription.retrieve(session['subscription'])
        tier = determine_tier_from_price(subscription['items']['data'][0]['price']['id'])
        
        user.subscription_tier = tier
        user.subscription_status = 'active'
        user.stripe_subscription_id = session['subscription']
        user.subscription_start_date = datetime.now()
        user.simulation_quota = get_quota_for_tier(tier)
        
        # Record transaction
        transaction = Transaction(
            user_id=user_id,
            stripe_payment_intent_id=session['payment_intent'],
            amount=session['amount_total'] / 100,
            currency=session['currency'],
            transaction_type='subscription',
            status='completed',
            completed_at=datetime.now()
        )
        
        db.add(transaction)
        db.commit()
        
    finally:
        db.close()
```

#### E. Streamlit Payment Page
```python
# Add to wealth_simulator.py or create payment.py
def show_payment_page():
    st.title("💳 Upgrade Your Plan")
    
    current_tier = st.session_state.get('subscription_tier', 'free')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🆓 Free")
        st.markdown("**$0/month**")
        st.markdown("✓ 10 simulations/month")
        st.markdown("✓ Basic features")
        st.markdown("✓ Export to Excel")
        if current_tier == 'free':
            st.info("Current Plan")
    
    with col2:
        st.subheader("⭐ Basic")
        st.markdown("**$4.99/month**")
        st.markdown("✓ 50 simulations/month")
        st.markdown("✓ All features")
        st.markdown("✓ PDF export")
        st.markdown("✓ Priority support")
        if st.button("Subscribe to Basic", key="basic"):
            checkout_url = create_checkout_session(
                st.session_state.user_id,
                'price_basic_monthly',
                f"{st.secrets['APP_URL']}/success",
                f"{st.secrets['APP_URL']}/cancel"
            )
            st.markdown(f"[Complete Payment]({checkout_url})")
    
    with col3:
        st.subheader("🚀 Pro")
        st.markdown("**$9.99/month**")
        st.markdown("✓ Unlimited simulations")
        st.markdown("✓ All features")
        st.markdown("✓ Advanced analytics")
        st.markdown("✓ API access")
        if st.button("Subscribe to Pro", key="pro"):
            checkout_url = create_checkout_session(
                st.session_state.user_id,
                'price_pro_monthly',
                f"{st.secrets['APP_URL']}/success",
                f"{st.secrets['APP_URL']}/cancel"
            )
            st.markdown(f"[Complete Payment]({checkout_url})")
    
    st.markdown("---")
    st.subheader("🎁 One-Time Purchases")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**25 Simulations Pack**")
        st.markdown("$2.99 one-time")
        if st.button("Buy Pack", key="pack_25"):
            # Create one-time payment
            pass
    
    with col_b:
        st.markdown("**Lifetime Access**")
        st.markdown("$49.99 one-time")
        if st.button("Buy Lifetime", key="lifetime"):
            # Create one-time payment
            pass
```


### 3. Alternative Payment Solutions

#### PayPal Subscriptions
- Good international coverage
- Higher fees (2.9% + $0.30)
- More complex integration than Stripe

#### Paddle
- Merchant of record (handles VAT/taxes)
- 5% + $0.50 per transaction
- Good for SaaS products
- Handles compliance automatically

#### LemonSqueezy
- Merchant of record
- 5% + $0.50 per transaction
- Simple integration
- Handles taxes and compliance


## 📊 Recommended Pricing Strategy

### Phase 1: Launch (Months 1-3)
**Goal:** Build user base, gather feedback

**Tiers:**
1. **Free** (Current)
   - 10 simulations/month
   - All core features
   - Excel export
   
2. **"Buy Me a Coffee" Donation**
   - Ko-fi button in header
   - Suggested amounts: $3, $5, $10
   - Optional: Manual verification for bonus simulations

**Why:** Low barrier to entry, build goodwill, test demand


### Phase 2: Soft Launch (Months 4-6)
**Goal:** Test pricing, establish value

**Tiers:**
1. **Free** - 10 sims/month
2. **Supporter** - $2.99/month
   - 30 simulations/month
   - Priority support
   - Early access to features
3. **One-time packs:**
   - 25 simulations: $2.99
   - 100 simulations: $9.99

**Why:** Low price point to test conversion, simple upsell


### Phase 3: Full Monetization (Months 7+)
**Goal:** Sustainable revenue

**Recommended Tiers:**

1. **Free** - $0/month
   - 10 simulations/month
   - Basic features
   - Excel export
   - Community support
   
2. **Basic** - $4.99/month or $49/year (17% savings)
   - 50 simulations/month
   - All features
   - PDF export
   - Email support
   - Budget builder access
   
3. **Pro** - $9.99/month or $99/year (17% savings)
   - Unlimited simulations
   - All features
   - Advanced analytics
   - Priority support
   - API access (future)
   - Custom scenarios
   
4. **Lifetime** - $149 one-time
   - Everything in Pro
   - Forever access
   - All future features
   - VIP support

**Add-ons:**
- Simulation packs (non-subscribers):
  - 25 sims: $2.99
  - 100 sims: $9.99
- Professional consultation: $99/hour


## 💡 Pricing Analysis

### Market Research Comparisons:

1. **Personal Capital** - Free (ad-supported)
2. **Empower** - Free basic, $89/year premium
3. **Tiller** - $79/year
4. **YNAB** - $99/year
5. **Mint** - Free (acquired by Credit Karma)

### Competitive Positioning:
- **Lower than competitors:** $49-99/year
- **Unique value:** Monte Carlo simulation + anonymized data insights
- **Target:** Personal finance enthusiasts, FIRE community


### Pricing Psychology:

**Why $4.99 vs $5.00?**
- Charm pricing effect (−1 cent)
- Perceived 25% discount on $6.66

**Why annual discount?**
- Reduces churn
- Predictable revenue
- Encourages commitment

**Why 17% savings?**
- Sweet spot for conversion
- Not too aggressive (sustainable)
- Clear value proposition


## 📈 Revenue Projections

### Conservative Scenario:
- 1,000 users after 6 months
- 3% conversion to paid ($4.99/mo)
- **Revenue:** 30 × $4.99 = $149.70/month ($1,796/year)

### Moderate Scenario:
- 5,000 users after 12 months
- 5% conversion to paid
- 60% on Basic ($4.99), 40% on Pro ($9.99)
- **Revenue:** ~$1,873/month ($22,476/year)

### Optimistic Scenario:
- 10,000 users after 18 months
- 8% conversion rate
- Mix of tiers + one-time purchases
- **Revenue:** ~$5,000/month ($60,000/year)


## 🎯 Implementation Roadmap

### Week 1-2: Quick Win
- [ ] Add Ko-fi donation button
- [ ] Track donations manually
- [ ] Thank donors publicly (opt-in)

### Month 1: Database Prep
- [ ] Add subscription fields to User model
- [ ] Create Transaction model
- [ ] Migration scripts
- [ ] Test locally

### Month 2: Stripe Integration
- [ ] Create Stripe account
- [ ] Set up products and prices
- [ ] Implement payment_integration.py
- [ ] Build payment page UI
- [ ] Test with Stripe test mode

### Month 3: Testing & Launch
- [ ] Beta test with 10 users
- [ ] Set up webhook endpoint
- [ ] Handle subscription renewals
- [ ] Implement customer portal
- [ ] Soft launch announcement

### Month 4+: Optimization
- [ ] A/B test pricing
- [ ] Add annual plans
- [ ] Implement referral program
- [ ] Analytics dashboard
- [ ] Customer feedback loop


## 🔒 Legal & Compliance

### Required:
1. **Terms of Service** ✅ (Already have)
2. **Privacy Policy** ✅ (Already have)
3. **Refund Policy**
   - 30-day money-back guarantee
   - No questions asked
   - Process via Stripe
   
4. **Tax Compliance**
   - Stripe Tax (automatic)
   - Or Paddle/LemonSqueezy (handles for you)
   
5. **GDPR Compliance** ✅ (Already compliant)


## 🎁 Alternative: Freemium Features

Instead of hard limits, consider feature gating:

**Free:**
- Basic Monte Carlo simulation
- 1 saved scenario
- Excel export

**Paid:**
- Budget builder integration
- Unlimited saved scenarios
- PDF export
- Multi-currency support
- Advanced analytics
- Custom events library
- Priority support


## 📊 Metrics to Track

1. **Conversion Funnel:**
   - Free signups
   - Payment page views
   - Checkout initiations
   - Completed purchases
   - Conversion rate %

2. **Revenue Metrics:**
   - MRR (Monthly Recurring Revenue)
   - ARR (Annual Recurring Revenue)
   - ARPU (Average Revenue Per User)
   - LTV (Lifetime Value)
   - Churn rate

3. **User Metrics:**
   - Active users
   - Simulations per user
   - Feature usage
   - Session length


## 🚀 Recommendation

**Start Simple → Iterate Based on Data**

1. **Week 1:** Add Ko-fi button ($0 cost, 1 hour work)
2. **Month 2:** If donations > $50/month, implement Stripe
3. **Month 3:** Launch Basic ($4.99) tier only
4. **Month 4:** Add Pro tier based on demand
5. **Month 6:** Introduce annual plans

**Initial Pricing:**
- Free: 10 sims/month
- Basic: $4.99/month (50 sims)
- Pro: $9.99/month (unlimited)

**Why this works:**
- Low risk (Ko-fi first)
- Data-driven decisions
- User feedback incorporated
- Gradual complexity increase
- Revenue grows with user base
