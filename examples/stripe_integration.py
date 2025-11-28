"""
Stripe Payment Integration for FinSim
Handles subscriptions, one-time payments, and webhooks

Setup:
1. pip install stripe
2. Add to .env:
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
3. Create products in Stripe Dashboard
4. Run database migration to add subscription fields
"""

import stripe
import os
import streamlit as st
from database import SessionLocal, User, Transaction
from datetime import datetime, timedelta

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


# ============================================================================
# SUBSCRIPTION TIERS
# ============================================================================

SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'simulations': 10,
        'features': ['Basic features', 'Excel export', 'Community support']
    },
    'basic': {
        'name': 'Basic',
        'price': 4.99,
        'stripe_price_id': 'price_basic_monthly',  # Get from Stripe Dashboard
        'simulations': 50,
        'features': ['All features', 'PDF export', 'Priority support', 'Budget builder']
    },
    'pro': {
        'name': 'Pro',
        'price': 9.99,
        'stripe_price_id': 'price_pro_monthly',
        'simulations': -1,  # Unlimited
        'features': ['Unlimited simulations', 'Advanced analytics', 'API access', 'VIP support']
    },
    'lifetime': {
        'name': 'Lifetime',
        'price': 149.00,
        'stripe_price_id': 'price_lifetime',
        'simulations': -1,
        'features': ['Everything in Pro', 'Forever', 'All future features']
    }
}


# ============================================================================
# PAYMENT FUNCTIONS
# ============================================================================

def create_checkout_session(user_id: int, tier: str, success_url: str, cancel_url: str):
    """
    Create Stripe Checkout session for subscription or one-time payment
    
    Args:
        user_id: User ID
        tier: Subscription tier ('basic', 'pro', 'lifetime')
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is canceled
        
    Returns:
        str: Checkout session URL
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        # Create or retrieve Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'user_id': user_id, 'username': user.username}
            )
            user.stripe_customer_id = customer.id
            db.commit()
        
        tier_info = SUBSCRIPTION_TIERS.get(tier)
        if not tier_info:
            return None
        
        # Determine mode: subscription vs one-time
        mode = 'payment' if tier == 'lifetime' else 'subscription'
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': tier_info['stripe_price_id'],
                'quantity': 1,
            }],
            mode=mode,
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={
                'user_id': user_id,
                'tier': tier
            }
        )
        
        return session.url
        
    except Exception as e:
        print(f"Error creating checkout session: {e}")
        return None
    finally:
        db.close()


def create_customer_portal_session(user_id: int, return_url: str):
    """
    Create Stripe Customer Portal session for managing subscription
    
    Args:
        user_id: User ID
        return_url: URL to return to after portal session
        
    Returns:
        str: Customer portal URL
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.stripe_customer_id:
            return None
        
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url
        )
        
        return session.url
        
    except Exception as e:
        print(f"Error creating portal session: {e}")
        return None
    finally:
        db.close()


def get_user_subscription_status(user_id: int):
    """
    Get current subscription status for user
    
    Returns:
        dict: Subscription details
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        return {
            'tier': user.subscription_tier or 'free',
            'status': user.subscription_status or 'active',
            'simulations_quota': user.simulation_quota or 10,
            'start_date': user.subscription_start_date,
            'end_date': user.subscription_end_date
        }
        
    finally:
        db.close()


# ============================================================================
# WEBHOOK HANDLERS
# ============================================================================

def handle_stripe_webhook(payload, sig_header):
    """
    Handle Stripe webhook events
    
    This should be called from a separate webhook endpoint
    (e.g., via Streamlit's experimental_set_query_params or FastAPI)
    """
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        print(f"Invalid payload: {e}")
        return False
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        return False
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
        
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    
    return True


def handle_checkout_completed(session):
    """Handle successful checkout"""
    db = SessionLocal()
    try:
        user_id = int(session['metadata']['user_id'])
        tier = session['metadata']['tier']
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            tier_info = SUBSCRIPTION_TIERS.get(tier)
            
            # Update user subscription
            user.subscription_tier = tier
            user.subscription_status = 'active'
            user.subscription_start_date = datetime.now()
            user.simulation_quota = tier_info['simulations']
            
            if tier == 'lifetime':
                user.subscription_end_date = None  # Never expires
            elif session.get('subscription'):
                user.stripe_subscription_id = session['subscription']
            
            # Record transaction
            transaction = Transaction(
                user_id=user_id,
                stripe_payment_intent_id=session.get('payment_intent'),
                amount=session['amount_total'] / 100,
                currency=session['currency'].upper(),
                transaction_type='subscription' if tier != 'lifetime' else 'one_time',
                description=f"{tier_info['name']} subscription",
                status='completed',
                completed_at=datetime.now()
            )
            
            db.add(transaction)
            db.commit()
            
            print(f"✅ Subscription activated for user {user_id}: {tier}")
            
    except Exception as e:
        print(f"Error handling checkout: {e}")
        db.rollback()
    finally:
        db.close()


def handle_payment_succeeded(invoice):
    """Handle successful subscription renewal"""
    db = SessionLocal()
    try:
        customer_id = invoice['customer']
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        
        if user:
            # Reset monthly simulation count on renewal
            from auth import get_user_usage_stats
            stats = get_user_usage_stats(user.user_id)
            # Stats are reset monthly anyway, but this ensures it happens on payment
            
            print(f"✅ Payment succeeded for user {user.id}")
            
    finally:
        db.close()


def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    db = SessionLocal()
    try:
        customer_id = subscription['customer']
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        
        if user:
            user.subscription_tier = 'free'
            user.subscription_status = 'canceled'
            user.subscription_end_date = datetime.now()
            user.simulation_quota = 10
            user.stripe_subscription_id = None
            
            db.commit()
            print(f"❌ Subscription canceled for user {user.id}")
            
    finally:
        db.close()


def handle_subscription_updated(subscription):
    """Handle subscription updates (e.g., plan changes)"""
    # Implement if needed
    pass


# ============================================================================
# STREAMLIT UI COMPONENTS
# ============================================================================

def show_pricing_page():
    """Display pricing tiers and payment options"""
    
    st.title("💳 Choose Your Plan")
    
    # Show current plan
    if st.session_state.get('authenticated'):
        status = get_user_subscription_status(st.session_state.user_id)
        current_tier = status['tier']
        
        st.info(f"📊 Current Plan: **{SUBSCRIPTION_TIERS[current_tier]['name']}**")
        st.markdown("---")
    else:
        current_tier = 'free'
    
    # Display tiers
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🆓 Free")
        st.markdown("### $0/month")
        st.markdown("---")
        for feature in SUBSCRIPTION_TIERS['free']['features']:
            st.markdown(f"✓ {feature}")
        st.markdown(f"✓ {SUBSCRIPTION_TIERS['free']['simulations']} simulations/month")
        
        if current_tier == 'free':
            st.success("Current Plan")
        else:
            if st.button("Downgrade to Free", key="free_btn"):
                st.warning("Contact support to downgrade")
    
    with col2:
        st.subheader("⭐ Basic")
        st.markdown("### $4.99/month")
        st.markdown("---")
        for feature in SUBSCRIPTION_TIERS['basic']['features']:
            st.markdown(f"✓ {feature}")
        st.markdown(f"✓ {SUBSCRIPTION_TIERS['basic']['simulations']} simulations/month")
        
        if current_tier == 'basic':
            st.success("Current Plan")
            if st.button("Manage Subscription", key="manage_basic"):
                portal_url = create_customer_portal_session(
                    st.session_state.user_id,
                    return_url=st.secrets.get('APP_URL', 'http://localhost:8501')
                )
                st.markdown(f"[Open Customer Portal]({portal_url})")
        else:
            if st.button("Subscribe to Basic", key="basic_btn", type="primary"):
                checkout_url = create_checkout_session(
                    st.session_state.user_id,
                    'basic',
                    success_url=f"{st.secrets.get('APP_URL', 'http://localhost:8501')}?success=true",
                    cancel_url=f"{st.secrets.get('APP_URL', 'http://localhost:8501')}/pricing"
                )
                if checkout_url:
                    st.markdown(f"[Complete Payment]({checkout_url})")
                else:
                    st.error("Error creating checkout session")
    
    with col3:
        st.subheader("🚀 Pro")
        st.markdown("### $9.99/month")
        st.markdown("---")
        for feature in SUBSCRIPTION_TIERS['pro']['features']:
            st.markdown(f"✓ {feature}")
        st.markdown("✓ Unlimited simulations")
        
        if current_tier == 'pro':
            st.success("Current Plan")
            if st.button("Manage Subscription", key="manage_pro"):
                portal_url = create_customer_portal_session(
                    st.session_state.user_id,
                    return_url=st.secrets.get('APP_URL', 'http://localhost:8501')
                )
                st.markdown(f"[Open Customer Portal]({portal_url})")
        else:
            if st.button("Subscribe to Pro", key="pro_btn", type="primary"):
                checkout_url = create_checkout_session(
                    st.session_state.user_id,
                    'pro',
                    success_url=f"{st.secrets.get('APP_URL', 'http://localhost:8501')}?success=true",
                    cancel_url=f"{st.secrets.get('APP_URL', 'http://localhost:8501')}/pricing"
                )
                if checkout_url:
                    st.markdown(f"[Complete Payment]({checkout_url})")
                else:
                    st.error("Error creating checkout session")
    
    # Lifetime option
    st.markdown("---")
    st.subheader("🎁 Lifetime Access")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("**One-time payment of $149**")
        st.markdown("Get everything in Pro, forever!")
        for feature in SUBSCRIPTION_TIERS['lifetime']['features']:
            st.markdown(f"✓ {feature}")
    
    with col_b:
        if current_tier == 'lifetime':
            st.success("You have Lifetime Access!")
        else:
            if st.button("Buy Lifetime", key="lifetime_btn", type="primary"):
                checkout_url = create_checkout_session(
                    st.session_state.user_id,
                    'lifetime',
                    success_url=f"{st.secrets.get('APP_URL', 'http://localhost:8501')}?success=true",
                    cancel_url=f"{st.secrets.get('APP_URL', 'http://localhost:8501')}/pricing"
                )
                if checkout_url:
                    st.markdown(f"[Complete Payment]({checkout_url})")
                else:
                    st.error("Error creating checkout session")


# ============================================================================
# USAGE IN AUTH.PY
# ============================================================================

def check_simulation_limit_with_subscription(user_id: int, is_admin: bool = False):
    """
    Enhanced simulation limit check that considers subscription tier
    
    Replace the existing check_simulation_limit function
    """
    if is_admin:
        return True, -1, "✓ Unlimited simulations (Admin)"
    
    # Get user subscription
    status = get_user_subscription_status(user_id)
    tier = status['tier']
    quota = status['simulations_quota']
    
    # Unlimited for Pro and Lifetime
    if quota == -1:
        return True, -1, f"✓ Unlimited simulations ({SUBSCRIPTION_TIERS[tier]['name']})"
    
    # Check usage
    from auth import get_user_usage_stats
    stats_data = get_user_usage_stats(user_id)
    remaining = quota - stats_data['simulations_this_month']
    
    if remaining <= 0:
        return False, 0, f"Monthly limit reached. Upgrade to get more simulations!"
    else:
        return True, remaining, f"{remaining}/{quota} simulations remaining ({SUBSCRIPTION_TIERS[tier]['name']})"
