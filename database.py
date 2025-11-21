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
    
    # Account status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    simulations = relationship("Simulation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


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


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()