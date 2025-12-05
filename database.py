"""
Database models and schema for FinSim wealth simulator
Uses SQLAlchemy ORM for database operations
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///finsim.db')

# Fix for Render PostgreSQL URL format (postgres:// → postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User account information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User profile data
    current_age = Column(Integer, nullable=True)
    target_retirement_age = Column(Integer, nullable=True)
    country = Column(String(100), nullable=True)
    
    # Spouse/partner data
    has_spouse = Column(Boolean, default=False)
    spouse_age = Column(Integer, nullable=True)
    spouse_retirement_age = Column(Integer, nullable=True)
    spouse_annual_income = Column(Float, nullable=True)  # Stored in base currency (EUR)
    
    # Account status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    simulations = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")
    passive_income_streams = relationship("PassiveIncomeStream", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class PassiveIncomeStream(Base):
    """Passive income streams (rental, dividends, royalties, etc.)"""
    __tablename__ = "passive_income_streams"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Stream details
    name = Column(String(255), nullable=False)  # e.g., "Rental Property", "Dividend Portfolio"
    income_type = Column(String(50), nullable=False, default='other')  # 'rental', 'dividend', 'royalty', 'business', 'other'
    description = Column(Text, nullable=True)
    
    # Amount (stored in base currency - EUR)
    monthly_amount = Column(Float, default=0)  # Monthly recurring amount
    
    # Lifecycle
    start_year = Column(Integer, default=0)  # Years from now (0 = starts immediately)
    end_year = Column(Integer, nullable=True)  # Optional end year (None = continues indefinitely)
    
    # Growth
    annual_growth_rate = Column(Float, default=0.02)  # Default 2% (inflation adjustment)
    
    # Tax treatment
    is_taxable = Column(Boolean, default=True)
    tax_rate = Column(Float, nullable=True)  # Optional override tax rate (uses effective_tax_rate if None)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="passive_income_streams")
    
    def __repr__(self):
        return f"<PassiveIncomeStream(id={self.id}, name='{self.name}', type='{self.income_type}')>"


class Simulation(Base):
    """Individual simulation run data"""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Simulation metadata
    name = Column(String(255), nullable=True)
    currency = Column(String(10), nullable=False)
    
    # Input parameters (anonymized for analysis)
    initial_liquid_wealth_bracket = Column(String(50), nullable=True)  # e.g., "100k-250k"
    initial_property_value_bracket = Column(String(50), nullable=True)
    income_bracket = Column(String(50), nullable=True)
    
    # Simulation configuration (full details for user)
    parameters = Column(JSON, nullable=True)  # All input parameters
    
    # Events summary (anonymized)
    has_property_purchase = Column(Boolean, default=False)
    has_property_sale = Column(Boolean, default=False)
    has_international_move = Column(Boolean, default=False)
    has_children = Column(Boolean, default=False)
    number_of_events = Column(Integer, default=0)
    
    # Results summary (anonymized)
    final_net_worth_bracket = Column(String(50), nullable=True)
    probability_of_success = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship back to user
    user = relationship("User", back_populates="simulations")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class AggregatedData(Base):
    """Aggregated anonymous data for research/analysis"""
    __tablename__ = "aggregated_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    period = Column(String(20), nullable=False, index=True)  # e.g., "2024-Q1"
    
    # Demographics (anonymized)
    age_range = Column(String(20), nullable=True)  # e.g., "30-35"
    country = Column(String(100), nullable=True)
    
    # Financial brackets
    wealth_bracket = Column(String(50), nullable=True)
    income_bracket = Column(String(50), nullable=True)
    
    # Behavior patterns
    avg_number_of_events = Column(Float, nullable=True)
    common_event_types = Column(JSON, nullable=True)  # ["property_purchase", "children"]
    
    # Planning metrics
    avg_planning_horizon = Column(Float, nullable=True)  # years
    median_retirement_age = Column(Integer, nullable=True)
    
    # Aggregated results
    median_final_net_worth_bracket = Column(String(50), nullable=True)
    avg_probability_of_success = Column(Float, nullable=True)
    
    # Sample size
    sample_size = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AggregatedData(period='{self.period}', sample_size={self.sample_size})>"


class UsageStats(Base):
    """Track usage for rate limiting and analytics"""
    __tablename__ = "usage_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Usage tracking
    simulations_this_month = Column(Integer, default=0)
    last_simulation_date = Column(DateTime(timezone=True), nullable=True)
    
    # Feature usage
    exports_this_month = Column(Integer, default=0)
    
    # Reset tracking
    current_month = Column(String(7), nullable=False)  # e.g., "2024-11"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UsageStats(user_id={self.user_id}, simulations={self.simulations_this_month})>"

class SavedBudget(Base):
    """Saved budget configurations with monthly tracking"""
    __tablename__ = "saved_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Budget metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    currency = Column(String(10), nullable=True)  # Currency code (EUR, USD, etc.)
    current_month = Column(String(7), nullable=True)  # Format: "2025-12" for tracking
    
    # Budget data (JSON) - New structure: {category: amount}
    budget_expected = Column(JSON, nullable=True)  # Expected monthly budget (nullable to match migration)
    
    # Monthly actuals (JSON) - New structure: {"2025-12": {category: amount}, "2026-01": {...}}
    budget_actuals = Column(JSON, nullable=True)  # Actual spending by month
    
    # Legacy fields (keep for backwards compatibility, will be NULL for new budgets)
    budget_now = Column(JSON, nullable=True)
    budget_min = Column(JSON, nullable=True)  # Minimum budget scenario
    budget_max = Column(JSON, nullable=True)  # Maximum budget scenario
    budget_target = Column(JSON, nullable=True)  # Target budget
    budget_1yr = Column(JSON, nullable=True)
    budget_5yr = Column(JSON, nullable=True)
    
    # Life events
    life_events = Column(JSON, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # User's default budget
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SavedBudget(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


class Feedback(Base):
    """User feedback and issue reports"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Nullable for anonymous submissions
    
    # Feedback details
    feedback_type = Column(String(50), nullable=False)  # 'bug', 'feature', 'general', 'issue'
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Context information
    page_context = Column(String(100), nullable=True)  # Which page/feature they were using
    user_email = Column(String(255), nullable=True)  # For follow-up
    
    # Status tracking
    status = Column(String(50), default='new')  # 'new', 'reviewed', 'resolved', 'closed'
    admin_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, type='{self.feedback_type}', status='{self.status}')>"


class PensionPlan(Base):
    """User pension planning data"""
    __tablename__ = "pension_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Plan metadata
    name = Column(String(255), default='My Pension Plan')
    country = Column(String(50), default='UK')  # For future expansion
    
    # Personal details
    date_of_birth = Column(String(10), nullable=True)  # YYYY-MM-DD format
    employment_start_age = Column(Integer, default=18)
    target_retirement_age = Column(Integer, default=67)
    
    # State Pension (UK)
    state_pension_enabled = Column(Boolean, default=True)
    state_pension_ni_years = Column(Integer, default=0)
    state_pension_projected_years = Column(Integer, default=0)
    state_pension_annual_amount = Column(Float, default=0)
    
    # USS Pension (Universities Superannuation Scheme)
    uss_enabled = Column(Boolean, default=False)
    uss_current_salary = Column(Float, default=0)
    uss_years_in_scheme = Column(Integer, default=0)
    uss_projected_annual_pension = Column(Float, default=0)
    uss_projected_lump_sum = Column(Float, default=0)
    uss_avc_enabled = Column(Boolean, default=False)
    uss_avc_annual_amount = Column(Float, default=0)
    uss_avc_percentage = Column(Float, default=0)
    uss_avc_current_value = Column(Float, default=0)
    uss_avc_projected_value = Column(Float, default=0)
    
    # SIPP (Self-Invested Personal Pension)
    sipp_enabled = Column(Boolean, default=False)
    sipp_current_value = Column(Float, default=0)
    sipp_annual_contribution = Column(Float, default=0)
    sipp_employer_contribution = Column(Float, default=0)
    sipp_projected_value = Column(Float, default=0)
    sipp_growth_rate = Column(Float, default=0.05)  # 5% default
    
    # Other pensions (workplace, private, etc.)
    other_pensions = Column(JSON, nullable=True)  # List of other pension schemes
    
    # Spouse/Partner pension planning
    spouse_enabled = Column(Boolean, default=False)
    spouse_age = Column(Integer, nullable=True)
    spouse_retirement_age = Column(Integer, nullable=True)
    spouse_annual_income = Column(Float, default=0)
    
    # Spouse State Pension
    spouse_state_pension_enabled = Column(Boolean, default=False)
    spouse_state_pension_ni_years = Column(Integer, default=0)
    spouse_state_pension_projected_years = Column(Integer, default=0)
    spouse_state_pension_annual_amount = Column(Float, default=0)
    
    # Spouse USS Pension
    spouse_uss_enabled = Column(Boolean, default=False)
    spouse_uss_current_salary = Column(Float, default=0)
    spouse_uss_years_in_scheme = Column(Integer, default=0)
    spouse_uss_projected_annual_pension = Column(Float, default=0)
    spouse_uss_projected_lump_sum = Column(Float, default=0)
    spouse_uss_avc_enabled = Column(Boolean, default=False)
    spouse_uss_avc_annual_amount = Column(Float, default=0)
    spouse_uss_avc_current_value = Column(Float, default=0)
    spouse_uss_avc_projected_value = Column(Float, default=0)
    
    # Spouse SIPP
    spouse_sipp_enabled = Column(Boolean, default=False)
    spouse_sipp_current_value = Column(Float, default=0)
    spouse_sipp_annual_contribution = Column(Float, default=0)
    spouse_sipp_employer_contribution = Column(Float, default=0)
    spouse_sipp_projected_value = Column(Float, default=0)
    spouse_sipp_growth_rate = Column(Float, default=0.05)
    
    # Retirement income planning
    desired_retirement_income = Column(Float, default=0)  # Annual amount desired
    expected_total_pension_income = Column(Float, default=0)  # Calculated total
    simulation_end_age = Column(Integer, default=0)  # Age to end simulation (for retirement modeling)
    
    # Settings and preferences
    salary_growth_rate = Column(Float, default=0.02)  # 2% default
    inflation_rate = Column(Float, default=0.02)  # 2% default
    drawdown_rate = Column(Float, default=0.04)  # 4% safe withdrawal rate
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_calculated = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<PensionPlan(id={self.id}, user_id={self.user_id}, name='{self.name}')>"


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_wealth_bracket(amount):
    """Convert exact amount to bracket for anonymization"""
    if amount < 0:
        return "negative"
    elif amount < 25000:
        return "0-25k"
    elif amount < 50000:
        return "25k-50k"
    elif amount < 100000:
        return "50k-100k"
    elif amount < 250000:
        return "100k-250k"
    elif amount < 500000:
        return "250k-500k"
    elif amount < 1000000:
        return "500k-1M"
    elif amount < 2500000:
        return "1M-2.5M"
    elif amount < 5000000:
        return "2.5M-5M"
    else:
        return "5M+"


def get_income_bracket(income):
    """Convert exact income to bracket"""
    if income < 30000:
        return "0-30k"
    elif income < 50000:
        return "30k-50k"
    elif income < 75000:
        return "50k-75k"
    elif income < 100000:
        return "75k-100k"
    elif income < 150000:
        return "100k-150k"
    elif income < 200000:
        return "150k-200k"
    elif income < 300000:
        return "200k-300k"
    else:
        return "300k+"


def get_age_range(age):
    """Convert exact age to range"""
    if age < 25:
        return "under-25"
    elif age < 30:
        return "25-29"
    elif age < 35:
        return "30-34"
    elif age < 40:
        return "35-39"
    elif age < 45:
        return "40-44"
    elif age < 50:
        return "45-49"
    elif age < 55:
        return "50-54"
    elif age < 60:
        return "55-59"
    elif age < 65:
        return "60-64"
    else:
        return "65+"

def save_budget(user_id, name, budget_expected=None, budget_actuals=None, current_month=None, 
                life_events=None, description=None, currency='EUR',
                budget_now=None, budget_1yr=None, budget_5yr=None):  # Legacy params for backwards compat
    """Save a budget configuration (supports new monthly tracking and legacy format)"""
    db = SessionLocal()
    try:
        budget_data = {
            'user_id': user_id,
            'name': name,
            'description': description,
            'currency': currency,
            'life_events': life_events or []
        }
        
        # New format - monthly tracking
        if budget_expected is not None:
            budget_data['budget_expected'] = budget_expected
            budget_data['budget_actuals'] = budget_actuals or {}
            budget_data['current_month'] = current_month or datetime.now().strftime("%Y-%m")
            # Provide empty dicts for legacy fields to satisfy NOT NULL constraints
            budget_data['budget_now'] = budget_expected  # Use expected as baseline
            budget_data['budget_min'] = {}  # Empty - not used in new format
            budget_data['budget_max'] = {}  # Empty - not used in new format  
            budget_data['budget_target'] = {}  # Empty - not used in new format
            budget_data['budget_1yr'] = {}  # Empty - not used in new format
            budget_data['budget_5yr'] = {}  # Empty - not used in new format
        # Legacy format - keep for backwards compatibility
        elif budget_now is not None:
            budget_data['budget_now'] = budget_now
            budget_data['budget_1yr'] = budget_1yr
            budget_data['budget_5yr'] = budget_5yr
            # Also populate expected field for consistency
            budget_data['budget_expected'] = budget_now
            budget_data['budget_actuals'] = {}
            # Provide defaults for missing legacy fields
            budget_data['budget_min'] = budget_data.get('budget_min', {})
            budget_data['budget_max'] = budget_data.get('budget_max', {})
            budget_data['budget_target'] = budget_data.get('budget_target', {})
        else:
            return False, "No budget data provided"
        
        budget = SavedBudget(**budget_data)
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return True, budget.id
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def get_user_budgets(user_id, limit=10):
    """Get user's saved budgets"""
    db = SessionLocal()
    try:
        budgets = db.query(SavedBudget).filter(
            SavedBudget.user_id == user_id,
            SavedBudget.is_active == True
        ).order_by(SavedBudget.created_at.desc()).limit(limit).all()
        return budgets
    finally:
        db.close()


def load_budget(user_id, budget_id):
    """Load a specific budget by ID (supports both new and legacy formats)"""
    db = SessionLocal()
    try:
        budget = db.query(SavedBudget).filter(
            SavedBudget.id == budget_id,
            SavedBudget.user_id == user_id,
            SavedBudget.is_active == True
        ).first()
        
        if budget:
            result = {
                'id': budget.id,
                'name': budget.name,
                'description': budget.description,
                'currency': budget.currency or 'EUR',
                'life_events': budget.life_events or [],
                'created_at': budget.created_at.isoformat() if budget.created_at else None
            }
            
            # Check if new format (monthly tracking) or legacy format
            if budget.budget_expected is not None:
                # New format
                result['budget_expected'] = budget.budget_expected
                result['budget_actuals'] = budget.budget_actuals or {}
                result['current_month'] = budget.current_month
                result['format'] = 'monthly'
            else:
                # Legacy format
                result['budget_now'] = budget.budget_now
                result['budget_1yr'] = budget.budget_1yr
                result['budget_5yr'] = budget.budget_5yr
                result['format'] = 'legacy'
            
            return True, result
        else:
            return False, "Budget not found"
    except Exception as e:
        return False, str(e)
    finally:
        db.close()

def get_default_budget(user_id):
    """Get user's default budget"""
    db = SessionLocal()
    try:
        budget = db.query(SavedBudget).filter(
            SavedBudget.user_id == user_id,
            SavedBudget.is_default == True,
            SavedBudget.is_active == True
        ).first()
        return budget
    finally:
        db.close()


def set_default_budget(user_id, budget_id):
    """Set a budget as the user's default"""
    db = SessionLocal()
    try:
        # Unset all other defaults
        db.query(SavedBudget).filter(
            SavedBudget.user_id == user_id
        ).update({'is_default': False})
        
        # Set new default
        budget = db.query(SavedBudget).filter(
            SavedBudget.id == budget_id,
            SavedBudget.user_id == user_id,
            SavedBudget.is_active 
        ).first()
        
        if budget:
            budget.is_default = True
            db.commit()
            return True, "Default budget updated"
        else:
            return False, "Budget not found"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def delete_budget(user_id, budget_id):
    """Soft delete a budget"""
    db = SessionLocal()
    try:
        budget = db.query(SavedBudget).filter(
            SavedBudget.id == budget_id,
            SavedBudget.user_id == user_id
        ).first()
        
        if budget:
            budget.is_active = False
            db.commit()
            return True, "Budget deleted"
        else:
            return False, "Budget not found"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


# Passive Income Stream Functions
def create_passive_income_stream(user_id, name, income_type, monthly_amount, 
                                 start_year=0, end_year=None, annual_growth_rate=0.02,
                                 is_taxable=True, tax_rate=None, description=None):
    """Create a new passive income stream"""
    db = SessionLocal()
    try:
        stream = PassiveIncomeStream(
            user_id=user_id,
            name=name,
            income_type=income_type,
            monthly_amount=monthly_amount,
            start_year=start_year,
            end_year=end_year,
            annual_growth_rate=annual_growth_rate,
            is_taxable=is_taxable,
            tax_rate=tax_rate,
            description=description
        )
        db.add(stream)
        db.commit()
        db.refresh(stream)
        return True, stream.id
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def get_user_passive_income_streams(user_id):
    """Get all active passive income streams for a user"""
    db = SessionLocal()
    try:
        streams = db.query(PassiveIncomeStream).filter(
            PassiveIncomeStream.user_id == user_id,
            PassiveIncomeStream.is_active == True
        ).order_by(PassiveIncomeStream.start_year).all()
        return streams
    finally:
        db.close()


def update_passive_income_stream(stream_id, user_id, **kwargs):
    """Update a passive income stream"""
    db = SessionLocal()
    try:
        stream = db.query(PassiveIncomeStream).filter(
            PassiveIncomeStream.id == stream_id,
            PassiveIncomeStream.user_id == user_id,
            PassiveIncomeStream.is_active == True
        ).first()
        
        if stream:
            for key, value in kwargs.items():
                if hasattr(stream, key):
                    setattr(stream, key, value)
            db.commit()
            return True, "Stream updated"
        else:
            return False, "Stream not found"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def delete_passive_income_stream(stream_id, user_id):
    """Soft delete a passive income stream"""
    db = SessionLocal()
    try:
        stream = db.query(PassiveIncomeStream).filter(
            PassiveIncomeStream.id == stream_id,
            PassiveIncomeStream.user_id == user_id
        ).first()
        
        if stream:
            stream.is_active = False
            db.commit()
            return True, "Stream deleted"
        else:
            return False, "Stream not found"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def submit_contact_form(name, email, subject, message, user_id=None, include_system_info=False):
    """Submit a contact form message as feedback"""
    db = SessionLocal()
    try:
        # Map subject to feedback_type
        subject_mapping = {
            "General Inquiry": "general",
            "Technical Support": "issue",
            "Bug Report": "bug",
            "Feature Request": "feature",
            "Account Issue": "issue",
            "Data/Privacy Question": "general",
            "Partnership Inquiry": "general",
            "Other": "general"
        }
        
        feedback_type = subject_mapping.get(subject, "general")
        
        # Create formatted message with contact info
        formatted_message = f"From: {name}\nEmail: {email}\n\n{message}"
        
        if include_system_info:
            formatted_message += f"\n\n--- System Info Included ---"
        
        feedback = Feedback(
            user_id=user_id,  # None for anonymous submissions
            feedback_type=feedback_type,
            subject=subject,
            message=formatted_message,
            user_email=email,
            page_context="Contact Form",
            status="new"
        )
        
        db.add(feedback)
        db.commit()
        return True, "Message sent successfully!"
    except Exception as e:
        db.rollback()
        return False, f"Error submitting message: {str(e)}"
    finally:
        db.close()

        
if __name__ == "__main__":

    # Initialize database when run directly
    init_db()