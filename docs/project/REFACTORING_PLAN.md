# FinSim Repository Refactoring Plan

## Executive Summary

This document outlines a comprehensive refactoring of the FinSim repository from a flat structure to a modern, maintainable, production-ready architecture following Python and Streamlit best practices.

**Goals:**
- Clear separation of concerns
- Improved maintainability and scalability
- Better developer onboarding
- Production-ready for Render deployment
- 100% functional equivalence (no breaking changes)

---

## Current Structure Analysis

### Current State (Flat Structure)
```
FinSim/
├── wealth_simulator.py          # Main app (2888 lines!) - NEEDS REFACTORING
├── auth.py                       # Authentication (855 lines)
├── database.py                   # Database models
├── landing_page.py               # Landing page
├── budget_builder.py             # Budget feature
├── pension_planner.py            # Pension calculations
├── pension_ui.py                 # Pension UI
├── currency_manager.py           # Currency logic
├── currency_converter.py         # Currency conversion
├── email_service.py              # Email verification
├── data_tracking.py              # Simulation storage
├── analytics_module.py           # Analytics
├── admin_analytics.py            # Admin analytics
├── ui_enhancements.py            # UI utilities
├── performance_utils.py          # Performance helpers
├── static_pages/                 # Static content pages
├── migrations/                   # Database migrations (9 files)
├── migrate_*.py                  # 4 migration scripts in root
├── fix_*.py                      # 3 fix scripts in root
├── test_*.py                     # 4 test scripts in root
├── delete_users.py               # Admin script
├── verify_existing_users.py      # Admin script
├── view_database.py              # Admin script
├── export_analytics.py           # Admin script
├── examples/                     # Integration examples
├── docs/                         # Mixed documentation
├── assets/                       # Static assets
└── 15+ markdown files in root    # Documentation scattered
```

### Problems Identified
1. **Monolithic main file**: `wealth_simulator.py` is 2888 lines
2. **Mixed concerns**: Admin scripts, migrations, tests all in root
3. **Scattered documentation**: 15+ markdown files in root
4. **No clear entry point**: Main app buried in root
5. **Import complexity**: Flat imports everywhere
6. **Hard to navigate**: 50+ Python files in root
7. **Deprecated code mixed in**: `alt_landing_page.py`, `integration_guide_app.py`

---

## Proposed Structure

### New Directory Layout

```
FinSim/
├── README.md                          # Main readme (project overview)
├── LICENSE
├── requirements.txt
├── runtime.txt
├── render.yaml
├── .gitignore
├── .env.example
│
├── app/                               # 🎯 STREAMLIT APPLICATION
│   ├── Home.py                        # Main entry point (Streamlit convention)
│   ├── __init__.py
│   ├── pages/                         # Streamlit multi-page app
│   │   ├── __init__.py
│   │   ├── 01_💰_Wealth_Simulator.py
│   │   ├── 02_📊_Budget_Builder.py
│   │   ├── 03_🏦_Pension_Planner.py
│   │   └── 04_📈_Analytics.py
│   │
│   ├── components/                    # Reusable UI components
│   │   ├── __init__.py
│   │   ├── header.py                  # User header, navigation
│   │   ├── currency_widget.py         # Currency selector
│   │   ├── simulation_controls.py     # Simulation input controls
│   │   └── charts.py                  # Chart generation
│   │
│   └── static/                        # Static content pages
│       ├── __init__.py
│       ├── about.py
│       ├── contact.py
│       ├── privacy.py
│       ├── terms.py
│       └── docs.py
│
├── services/                          # 🔧 BUSINESS LOGIC
│   ├── __init__.py
│   ├── monte_carlo.py                 # Monte Carlo simulation engine
│   ├── pension_calculator.py          # Pension calculation logic
│   ├── budget_service.py              # Budget calculations
│   ├── analytics_service.py           # Analytics generation
│   ├── currency_service.py            # Currency conversion logic
│   ├── email_service.py               # Email sending (moved from root)
│   ├── export_service.py              # PDF/CSV export logic
│   └── simulation_service.py          # Simulation orchestration
│
├── auth/                              # 🔐 AUTHENTICATION
│   ├── __init__.py
│   ├── handlers.py                    # Login/register/logout
│   ├── session.py                     # Session management
│   ├── verification.py                # Email verification
│   └── middleware.py                  # Auth decorators
│
├── data/                              # 💾 DATA ACCESS LAYER
│   ├── __init__.py
│   ├── models.py                      # SQLAlchemy models (from database.py)
│   ├── session.py                     # Database session management
│   ├── repositories/                  # Repository pattern
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── simulation_repository.py
│   │   ├── budget_repository.py
│   │   └── analytics_repository.py
│   └── tracking.py                    # Data tracking (from data_tracking.py)
│
├── lib/                               # 📚 SHARED UTILITIES
│   ├── __init__.py
│   ├── currency.py                    # Currency utilities
│   ├── formatters.py                  # Number/date formatting
│   ├── validators.py                  # Input validation
│   ├── constants.py                   # App-wide constants
│   └── performance.py                 # Performance utilities
│
├── admin/                             # 🔧 ADMIN TOOLS
│   ├── __init__.py
│   ├── verify_users.py                # Verify existing users
│   ├── delete_users.py                # User deletion tool
│   ├── export_data.py                 # Data export (from export_analytics.py)
│   ├── view_database.py               # Database viewer
│   └── analytics_dashboard.py         # Admin analytics (from admin_analytics.py)
│
├── db/                                # 🗄️ DATABASE
│   ├── __init__.py
│   ├── init_db.py                     # Database initialization
│   ├── migrations/                    # All migration scripts
│   │   ├── __init__.py
│   │   ├── 001_add_uss_avc_fields.py
│   │   ├── 002_add_spouse_fields.py
│   │   ├── 003_add_passive_income_streams.py
│   │   ├── 004_add_simulation_end_age.py
│   │   ├── 005_add_feedback_table.py
│   │   ├── 006_add_monthly_budget_tracking.py
│   │   ├── 007_add_currency_column.py
│   │   ├── 008_make_legacy_budget_nullable.py
│   │   ├── 009_add_pension_plans_table.py
│   │   ├── 010_make_feedback_user_id_nullable.py
│   │   ├── 011_add_budget_columns.py
│   │   ├── 012_postgres_budget_columns.py
│   │   ├── 013_add_currency_to_budgets.py
│   │   └── 014_email_verification.py
│   │
│   └── scripts/                       # Database utility scripts
│       ├── sync_schema.py
│       └── run_migrations.sh
│
├── config/                            # ⚙️ CONFIGURATION
│   ├── __init__.py
│   ├── settings.py                    # App settings (from env vars)
│   ├── database.py                    # Database config
│   └── smtp.py                        # Email config
│
├── tests/                             # ✅ TESTS
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_monte_carlo.py
│   │   ├── test_currency.py
│   │   └── test_pension.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_simulation_flow.py
│   │   └── test_auth_flow.py
│   └── fixtures/
│       └── test_data.py
│
├── deprecated/                        # 🗑️ DEPRECATED CODE
│   ├── README.md                      # Explains what's here and why
│   ├── scripts/
│   │   ├── alt_landing_page.py
│   │   ├── integration_guide_app.py
│   │   └── INTEGRATION_SNIPPETS.py
│   └── fixes/
│       ├── fix_render_spouse_fields.py
│       ├── fix_render_db.py
│       └── fix_render_all_migrations.py
│
├── docs/                              # 📖 DOCUMENTATION
│   ├── README.md                      # Docs index
│   ├── user/                          # User documentation
│   │   ├── getting_started.md
│   │   ├── features.md
│   │   ├── email_verification.md     # From EMAIL_VERIFICATION_QUICKSTART.md
│   │   └── faq.md
│   │
│   ├── dev/                           # Developer documentation
│   │   ├── setup.md
│   │   ├── architecture.md
│   │   ├── contributing.md           # From CONTRIBUTING.md
│   │   ├── database.md               # Database schema docs
│   │   ├── deployment.md             # Deployment guide
│   │   ├── api.md                    # Internal API docs
│   │   └── troubleshooting.md
│   │
│   └── operations/                    # Ops/admin documentation
│       ├── database_access.md        # From DATABASE_ACCESS_GUIDE.md
│       ├── render_deployment.md      # From DEPLOYMENT_GUIDE.md
│       ├── render_pricing.md         # From RENDER_PRICING.md
│       ├── social_media.md           # From SOCIAL_MEDIA_SETUP.md
│       └── fixes/                    # Historical fix documentation
│           ├── database_fix.md
│           ├── pdf_export_fix.md
│           ├── quick_fixes.md
│           └── session_persistence.md
│
├── assets/                            # 🎨 STATIC ASSETS
│   ├── favicon.png
│   ├── logo.png
│   └── images/
│
├── scripts/                           # 🛠️ UTILITY SCRIPTS
│   ├── local_dev.sh                   # Local development
│   ├── render_build.sh                # Render build script
│   └── test_email.sh                  # Email testing
│
├── exports/                           # 📁 GENERATED EXPORTS
│   └── .gitkeep
│
└── .streamlit/                        # Streamlit config
    └── config.toml
```

---

## Directory Responsibilities

### `/app/` - Streamlit Application
**Purpose**: All Streamlit UI code, pages, and components

**Contains**:
- `Home.py` - Main entry point (replaces `landing_page.py` + routing)
- `pages/` - Streamlit multi-page structure
- `components/` - Reusable UI components
- `static/` - Static content pages (moved from `static_pages/`)

**Imports from**: `services/`, `auth/`, `data/`, `lib/`

**Principles**:
- Each page is self-contained
- Components are reusable across pages
- Minimal business logic (delegate to services)
- Streamlit-specific code only

---

### `/services/` - Business Logic Layer
**Purpose**: Core business logic, calculations, and algorithms

**Contains**:
- `monte_carlo.py` - Monte Carlo simulation engine (extracted from `wealth_simulator.py`)
- `pension_calculator.py` - Pension calculations (from `pension_planner.py`)
- `budget_service.py` - Budget logic (from `budget_builder.py`)
- `currency_service.py` - Currency operations (from `currency_manager.py` + `currency_converter.py`)
- `email_service.py` - Email operations (moved from root)
- `export_service.py` - PDF/CSV export logic
- `analytics_service.py` - Analytics generation (from `analytics_module.py`)

**Imports from**: `data/`, `lib/`, `config/`

**Principles**:
- Pure Python (no Streamlit dependencies)
- Testable functions
- Single responsibility
- Can be used by CLI, API, or UI

---

### `/auth/` - Authentication Module
**Purpose**: User authentication, session management, email verification

**Contains**:
- `handlers.py` - Login, register, logout functions (from `auth.py`)
- `session.py` - Session state management
- `verification.py` - Email verification logic
- `middleware.py` - Auth decorators and checks

**Imports from**: `data/`, `services/email_service.py`, `config/`

**Principles**:
- Security-focused
- Stateless where possible
- Clear error messages
- Audit logging ready

---

### `/data/` - Data Access Layer
**Purpose**: Database models, repositories, and data access

**Contains**:
- `models.py` - SQLAlchemy models (from `database.py`)
- `session.py` - Database session factory
- `repositories/` - Repository pattern for each entity
- `tracking.py` - Simulation tracking (from `data_tracking.py`)

**Imports from**: `config/`

**Principles**:
- Repository pattern for data access
- No business logic
- Database-agnostic where possible
- Transaction management

---

### `/lib/` - Shared Utilities
**Purpose**: Reusable utilities and helpers

**Contains**:
- `currency.py` - Currency formatting and conversion helpers
- `formatters.py` - Number, date, string formatters
- `validators.py` - Input validation
- `constants.py` - App-wide constants
- `performance.py` - Performance utilities (from `performance_utils.py`)

**Imports from**: Nothing (standalone utilities)

**Principles**:
- Pure functions
- Well-tested
- No external dependencies where possible
- Comprehensive docstrings

---

### `/admin/` - Admin Tools
**Purpose**: Administrative scripts and tools

**Contains**:
- `verify_users.py` - Verify existing users (from root)
- `delete_users.py` - User deletion (from root)
- `export_data.py` - Data export (from `export_analytics.py`)
- `view_database.py` - Database viewer (from root)
- `analytics_dashboard.py` - Admin analytics (from `admin_analytics.py`)

**Imports from**: `data/`, `services/`, `config/`

**Principles**:
- CLI-first
- Interactive prompts
- Safety checks (confirmations)
- Logging all actions

---

### `/db/` - Database Management
**Purpose**: Database initialization, migrations, and scripts

**Contains**:
- `init_db.py` - Database initialization
- `migrations/` - Numbered migration files
- `scripts/` - Utility scripts

**Imports from**: `data/models.py`, `config/`

**Principles**:
- Numbered migrations
- Idempotent operations
- Both SQLite and PostgreSQL support
- Rollback capability

---

### `/config/` - Configuration
**Purpose**: Application configuration from environment variables

**Contains**:
- `settings.py` - Main app settings
- `database.py` - Database configuration
- `smtp.py` - Email/SMTP configuration

**Imports from**: Nothing (reads from env vars)

**Principles**:
- 12-factor app compliant
- Type validation
- Sensible defaults
- Environment-based overrides

---

### `/tests/` - Test Suite
**Purpose**: Automated tests

**Contains**:
- `unit/` - Unit tests
- `integration/` - Integration tests
- `fixtures/` - Test data

**Imports from**: Everything

**Principles**:
- Pytest framework
- High coverage (>80%)
- Fast unit tests
- Isolated integration tests

---

### `/deprecated/` - Deprecated Code
**Purpose**: Code no longer in use but kept for reference

**Contains**:
- Old scripts
- Prototypes
- Legacy implementations
- One-time fixes

**Principles**:
- Never imported by production code
- Documented reason for deprecation
- Can be deleted after 6 months

---

### `/docs/` - Documentation
**Purpose**: All project documentation

**Structure**:
- `user/` - End-user documentation
- `dev/` - Developer documentation
- `operations/` - Operations and deployment docs

**Principles**:
- Markdown format
- Clear hierarchy
- Keep updated with code changes
- Link from README

---

### `/scripts/` - Utility Scripts
**Purpose**: Development and deployment scripts

**Contains**:
- Build scripts
- Development helpers
- Test runners

**Principles**:
- Shell scripts for common tasks
- Documented with comments
- Error handling

---

## Migration Strategy

### Phase 1: Preparation (No Code Changes)
1. Create new directory structure
2. Copy files to new locations (keep originals)
3. Update imports in copied files
4. Create `__init__.py` files
5. Create migration checklist

### Phase 2: Core Refactoring
1. Split `wealth_simulator.py`:
   - Extract Monte Carlo logic → `services/monte_carlo.py`
   - Extract UI → `app/pages/01_💰_Wealth_Simulator.py`
   - Extract utilities → `lib/`
   - Create `app/Home.py` entry point

2. Reorganize authentication:
   - Split `auth.py` → `auth/` module
   - Extract email verification → `auth/verification.py`

3. Reorganize data layer:
   - Move `database.py` → `data/models.py`
   - Move `data_tracking.py` → `data/tracking.py`
   - Create repository classes

4. Reorganize services:
   - Move service files to `services/`
   - Update imports

5. Move admin tools:
   - Move admin scripts to `admin/`

6. Consolidate migrations:
   - Rename and number migrations
   - Move to `db/migrations/`

### Phase 3: Testing
1. Run all tests
2. Test each page manually
3. Test authentication flow
4. Test admin tools
5. Verify Render deployment

### Phase 4: Cleanup
1. Delete old files from root
2. Update documentation
3. Update README
4. Clean up imports

### Phase 5: Deployment
1. Update `render.yaml`
2. Update build script
3. Test on Render
4. Monitor for issues

---

## Updated Import Paths

### Before → After Examples

```python
# Before
from auth import initialize_session_state, show_login_page
from database import SessionLocal, User
from data_tracking import save_simulation
from currency_manager import format_currency
from email_service import send_verification_email

# After
from auth.session import initialize_session_state
from auth.handlers import show_login_page
from data.models import User
from data.session import SessionLocal
from data.tracking import save_simulation
from lib.currency import format_currency
from services.email_service import send_verification_email
```

### Import Guidelines

1. **Absolute imports** from project root
2. **Relative imports** within same module
3. **Lazy imports** for heavy dependencies
4. **Type hints** using `from __future__ import annotations`

---

## Render Deployment Updates

### New `render.yaml`

```yaml
services:
  - type: web
    name: finsim-app
    env: python
    runtime: python
    plan: starter
    buildCommand: ./scripts/render_build.sh
    startCommand: streamlit run app/Home.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: finsim-db
          property: connectionString
      # ... other env vars
```

### New `scripts/render_build.sh`

```bash
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running database migrations..."
python -m db.migrations.run_all

echo "Build complete!"
```

---

## Migration Checklist

### Pre-Migration
- [ ] Create new branch: `git checkout -b refactor/project-structure`
- [ ] Backup database
- [ ] Document current deployment state
- [ ] Run all existing tests and record results
- [ ] Tag current version: `git tag v1.0-pre-refactor`

### Directory Setup
- [ ] Create all new directories
- [ ] Add `__init__.py` to all Python packages
- [ ] Create `.gitkeep` for empty directories

### Core Files
- [ ] Split `wealth_simulator.py` → `services/monte_carlo.py` + `app/pages/01_*`
- [ ] Create `app/Home.py` (entry point)
- [ ] Move `auth.py` → `auth/` module
- [ ] Move `database.py` → `data/models.py`
- [ ] Move `data_tracking.py` → `data/tracking.py`

### Services
- [ ] Move `email_service.py` → `services/`
- [ ] Move `pension_planner.py` → `services/pension_calculator.py`
- [ ] Move `budget_builder.py` logic → `services/budget_service.py`
- [ ] Move `currency_manager.py` + `currency_converter.py` → `services/currency_service.py`
- [ ] Move `analytics_module.py` → `services/analytics_service.py`
- [ ] Create `services/export_service.py` (extract from wealth_simulator.py)

### UI/Components
- [ ] Move `landing_page.py` logic → `app/Home.py`
- [ ] Move `static_pages/` → `app/static/`
- [ ] Create `app/components/header.py` (extract from auth.py)
- [ ] Create `app/components/charts.py` (extract from wealth_simulator.py)
- [ ] Create `app/pages/02_📊_Budget_Builder.py`
- [ ] Create `app/pages/03_🏦_Pension_Planner.py`
- [ ] Create `app/pages/04_📈_Analytics.py`

### Utilities
- [ ] Extract currency utils → `lib/currency.py`
- [ ] Extract formatters → `lib/formatters.py`
- [ ] Extract validators → `lib/validators.py`
- [ ] Move `performance_utils.py` → `lib/performance.py`
- [ ] Create `lib/constants.py`

### Data Layer
- [ ] Create `data/session.py`
- [ ] Create `data/repositories/user_repository.py`
- [ ] Create `data/repositories/simulation_repository.py`
- [ ] Create `data/repositories/budget_repository.py`
- [ ] Create `data/repositories/analytics_repository.py`

### Configuration
- [ ] Create `config/settings.py`
- [ ] Create `config/database.py`
- [ ] Create `config/smtp.py`
- [ ] Update `.env.example`

### Admin Tools
- [ ] Move `verify_existing_users.py` → `admin/verify_users.py`
- [ ] Move `delete_users.py` → `admin/`
- [ ] Move `export_analytics.py` → `admin/export_data.py`
- [ ] Move `view_database.py` → `admin/`
- [ ] Move `admin_analytics.py` → `admin/analytics_dashboard.py`

### Database
- [ ] Create `db/init_db.py`
- [ ] Rename and move migrations to `db/migrations/`
- [ ] Number migrations sequentially
- [ ] Create `db/scripts/run_migrations.sh`
- [ ] Test migration rollback

### Tests
- [ ] Move `test_*.py` → `tests/unit/`
- [ ] Create test fixtures
- [ ] Add integration tests
- [ ] Update test imports
- [ ] Verify all tests pass

### Deprecated
- [ ] Move `alt_landing_page.py` → `deprecated/scripts/`
- [ ] Move `integration_guide_app.py` → `deprecated/scripts/`
- [ ] Move `INTEGRATION_SNIPPETS.py` → `deprecated/scripts/`
- [ ] Move `fix_*.py` → `deprecated/fixes/`
- [ ] Create `deprecated/README.md`

### Documentation
- [ ] Consolidate markdown files → `docs/`
- [ ] Create `docs/user/` structure
- [ ] Create `docs/dev/` structure
- [ ] Create `docs/operations/` structure
- [ ] Update main `README.md`
- [ ] Create `docs/README.md` (index)

### Scripts
- [ ] Move `local_dev.sh` → `scripts/`
- [ ] Move `render-build-with-meta.sh` → `scripts/render_build.sh`
- [ ] Create `scripts/test_email.sh`

### Configuration Files
- [ ] Update `render.yaml` (new entry point)
- [ ] Update `.gitignore`
- [ ] Verify `.streamlit/config.toml`

### Testing Phase
- [ ] Test `app/Home.py` loads correctly
- [ ] Test each page in `app/pages/`
- [ ] Test login/register flow
- [ ] Test email verification
- [ ] Test simulation save/load
- [ ] Test budget features
- [ ] Test pension calculator
- [ ] Test admin tools
- [ ] Test all imports resolve
- [ ] Run linter (flake8/ruff)
- [ ] Run type checker (mypy)
- [ ] Run test suite
- [ ] Test locally with `streamlit run app/Home.py`

### Deployment
- [ ] Test Render deployment in staging
- [ ] Verify database migrations run
- [ ] Verify environment variables work
- [ ] Smoke test all features
- [ ] Monitor logs for errors
- [ ] Deploy to production

### Cleanup
- [ ] Delete old files from root
- [ ] Remove unused imports
- [ ] Clean up `__pycache__` directories
- [ ] Remove old migration files
- [ ] Remove duplicate markdown files

### Post-Migration
- [ ] Update all documentation
- [ ] Create architecture diagram
- [ ] Document new import patterns
- [ ] Update contributing guide
- [ ] Tag new version: `git tag v2.0-refactored`
- [ ] Create release notes

---

## Key Implementation Files

### 1. `app/Home.py` (New Entry Point)

```python
"""
FinSim - Financial Simulation Toolkit
Main entry point for the Streamlit application
"""

import streamlit as st
from auth.session import initialize_session_state
from auth.handlers import show_login_page
from app.components.header import show_landing_page
from data.models import init_db

# Page configuration
st.set_page_config(
    page_title="FinSTK - Financial Simulation Toolkit",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Initialize session state
initialize_session_state()

# Authentication check
if not st.session_state.get('authenticated', False):
    show_landing_page()
    st.stop()

# User is authenticated - show navigation
show_user_header()

# Main content
st.title("🎯 FinSTK - Financial Simulation Toolkit")
st.markdown("""
Welcome to your personal financial planning toolkit!

Choose a tool from the sidebar:
- 💰 **Wealth Simulator** - Monte Carlo wealth projections
- 📊 **Budget Builder** - Track and plan your budget
- 🏦 **Pension Planner** - UK pension calculations
- 📈 **Analytics** - View your financial data
""")
```

### 2. `config/settings.py`

```python
"""
Application settings loaded from environment variables
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# App Settings
APP_NAME = "FinSTK"
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///finsim.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

# Simulation Limits
FREE_SIMULATION_LIMIT = int(os.getenv("FREE_SIMULATION_LIMIT", "10"))

# Base URL
BASE_URL = os.getenv("BASE_URL", "http://localhost:8501")

# Feature Flags
ENABLE_PDF_EXPORT = os.getenv("ENABLE_PDF_EXPORT", "True").lower() == "true"
ENABLE_EMAIL_VERIFICATION = os.getenv("ENABLE_EMAIL_VERIFICATION", "True").lower() == "true"
```

### 3. `data/repositories/user_repository.py`

```python
"""
User repository for data access
"""

from typing import Optional
from sqlalchemy.orm import Session
from data.models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
```

---

## GitHub-Ready README Structure

```markdown
# FinSTK - Financial Simulation Toolkit

> Monte Carlo wealth simulations, budget planning, and UK pension calculators

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)

## 🚀 Quick Start

[Installation](#installation) | [Documentation](#documentation) | [Contributing](#contributing) | [Deployment](#deployment)

## 📖 About

FinSTK is a comprehensive financial planning toolkit that helps you:
- 💰 Run Monte Carlo wealth simulations
- 📊 Build and track budgets
- 🏦 Calculate UK pensions (State, USS, SIPP)
- 💱 Plan in multiple currencies
- 📈 Visualize your financial future

## ✨ Features

- **Monte Carlo Simulations**: Probability-based wealth projections
- **Budget Builder**: Monthly expense tracking and planning
- **Pension Calculators**: State Pension, USS, and SIPP
- **Multi-Currency**: Support for 15+ currencies
- **PDF Export**: Professional simulation reports
- **Secure**: Email verification and session management

## 🛠️ Installation

### Local Development

```bash
# Clone repository
git clone https://github.com/Nialljb/FinSim.git
cd FinSim

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python -m db.scripts.run_migrations

# Start app
streamlit run app/Home.py
```

### Docker (Coming Soon)

## 📚 Documentation

- [User Guide](docs/user/) - How to use FinSTK
- [Developer Guide](docs/dev/) - Contributing and architecture
- [API Documentation](docs/dev/api.md) - Internal APIs
- [Deployment Guide](docs/operations/render_deployment.md) - Deploy to Render

## 🏗️ Architecture

```
FinSim/
├── app/              # Streamlit UI
├── services/         # Business logic
├── auth/             # Authentication
├── data/             # Data access layer
├── lib/              # Shared utilities
└── config/           # Configuration
```

See [Architecture Documentation](docs/dev/architecture.md) for details.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=services --cov=auth

# Run specific test file
pytest tests/unit/test_monte_carlo.py
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/dev/contributing.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Monte Carlo methodology based on [Understanding Monte Carlo Simulation](docs/user/monte_carlo.md)
- UK pension rules from official government sources
- Currency data from exchange rate APIs

## 📞 Support

- 📧 Email: support@finstk.com
- 📖 Documentation: [docs/](docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/Nialljb/FinSim/issues)

---

Made with ❤️ by the FinSTK team
```

---

## CI/CD Improvements

### GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 mypy
    
    - name: Lint with flake8
      run: flake8 app/ services/ auth/ data/ lib/
    
    - name: Type check with mypy
      run: mypy app/ services/ auth/ data/ lib/ --ignore-missing-imports
    
    - name: Run tests
      run: pytest --cov=app --cov=services --cov=auth --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      uses: pypa/gh-action-pip-audit@v1.0.0
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: ['--max-line-length=120']
```

---

## Risk Assessment

### Low Risk
- Moving files to new directories
- Creating new `__init__.py` files
- Updating documentation
- Adding tests

### Medium Risk
- Splitting large files (wealth_simulator.py)
- Changing import paths
- Refactoring authentication module
- Repository pattern implementation

### High Risk
- Database model changes
- Migration consolidation
- Render deployment changes
- Entry point change (wealth_simulator.py → app/Home.py)

### Mitigation Strategies
1. **Feature branch**: All work on `refactor/project-structure`
2. **Staging environment**: Test on Render staging before production
3. **Rollback plan**: Keep old structure until fully tested
4. **Incremental deployment**: Deploy one module at a time
5. **Monitoring**: Enhanced logging during transition
6. **Backup**: Database backup before migration

---

## Timeline Estimate

### Week 1: Preparation
- Day 1-2: Create directory structure, move files
- Day 3-4: Update imports in new locations
- Day 5: Create `__init__.py` files, initial testing

### Week 2: Core Refactoring
- Day 1-2: Split `wealth_simulator.py`
- Day 3: Refactor authentication module
- Day 4: Reorganize data layer
- Day 5: Testing and bug fixes

### Week 3: Services & Utilities
- Day 1-2: Move and refactor services
- Day 3: Create utility modules
- Day 4: Admin tools migration
- Day 5: Testing

### Week 4: Testing & Documentation
- Day 1-2: Comprehensive testing
- Day 3: Documentation updates
- Day 4: Staging deployment
- Day 5: Production deployment

**Total: 4 weeks** (20 working days)

---

## Success Criteria

- [ ] All existing features work identically
- [ ] No broken imports
- [ ] All tests pass
- [ ] Render deployment successful
- [ ] Documentation updated
- [ ] Code coverage maintained or improved
- [ ] No performance degradation
- [ ] Developer onboarding time reduced by 50%
- [ ] File navigation time reduced by 70%

---

## Conclusion

This refactoring will transform FinSim from a prototype into a production-ready, maintainable application. The new structure follows industry best practices, improves developer experience, and sets the foundation for long-term growth.

**Next Steps:**
1. Review this plan with the team
2. Create feature branch
3. Start with Phase 1 (Preparation)
4. Execute migration checklist systematically
5. Test thoroughly before deployment

---

*Generated: 2025-12-06*
*Author: Software Architecture Team*
*Version: 1.0*
