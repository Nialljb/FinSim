# Deprecated Code

This directory contains code that is no longer actively used in the FinSim application but is kept for historical reference.

## Structure

- `scripts/` - Old prototype scripts and alternative implementations
- `fixes/` - One-time fix scripts for historical database/deployment issues

## Contents

### Scripts
- `alt_landing_page.py` - Alternative landing page implementation (superseded by current landing_page.py)
- `integration_guide_app.py` - Integration guide prototype (superseded by documentation)
- `INTEGRATION_SNIPPETS.py` - Code snippets for integration (moved to docs)

### Fixes
- `fix_render_spouse_fields.py` - One-time fix for spouse fields migration on Render
- `fix_render_db.py` - One-time database fix for Render deployment
- `fix_render_all_migrations.py` - Migration consolidation fix for Render

## Policy

**Do NOT import any code from this directory in production code.**

Files in this directory:
- Are kept for historical reference only
- May be deleted after 6 months if not needed
- Should be documented with reason for deprecation
- Must not be dependencies for current features

## Deprecation Date

Most files deprecated during refactoring: December 6, 2025

## Questions?

See the main project documentation or contact the development team.
