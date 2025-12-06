# Database Migrations

This directory contains database migration scripts for FinSim.

## Quick Fix for Render - Spouse Fields Error

If you're seeing the error: `column users.has_spouse does not exist`

### Run via Render Shell (Recommended)

1. Go to your Render dashboard
2. Navigate to your Web Service
3. Click "Shell" in the left menu
4. Run:
   ```bash
   python fix_render_spouse_fields.py
   ```

This will add all missing spouse-related columns to the users table.

---

## Quick Fix for Render - Currency Column Error

If you're seeing the error: `column saved_budgets.currency does not exist`

### Option 1: Run via Render Shell (Recommended)

1. Go to your Render dashboard
2. Navigate to your Web Service
3. Click "Shell" in the left menu
4. Run:
   ```bash
   python fix_render_db.py
   ```

### Option 2: Run as One-Time Job

1. In Render dashboard, go to your service
2. Click "Manual Deploy" → "Clear build cache & deploy"
3. Or create a one-time job that runs:
   ```bash
   python fix_render_db.py
   ```

### Option 3: Local Connection to Render DB

If you have the Render database credentials:

```bash
# Set the DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@host/database"

# Run the fix
python fix_render_db.py
```

## Migration Scripts

### `fix_render_db.py`
Quick fix for the missing `currency` column. Minimal dependencies, safe to run multiple times.

**Usage:**
```bash
python fix_render_db.py
```

### `add_currency_column.py`
Standalone migration to add the currency column with validation checks.

**Usage:**
```bash
python migrations/add_currency_column.py
```

### `sync_schema.py`
Comprehensive schema synchronization tool. Compares your SQLAlchemy models with the actual database and adds any missing columns.

**Usage:**
```bash
python migrations/sync_schema.py
```

**Features:**
- Detects missing tables and creates them
- Identifies missing columns across all tables
- Shows a preview of changes before applying
- Interactive confirmation prompt
- Detailed logging of all changes

## When to Run Migrations

Run migrations when:

1. **After deploying code with new database columns** - The SQLAlchemy models update automatically in code, but the database schema needs manual updates
2. **When seeing "column does not exist" errors** - Indicates a schema mismatch
3. **After pulling changes that modify database models** - Check if new columns were added
4. **When setting up a new environment** - Use `sync_schema.py` to ensure everything is up to date

## Safety Notes

✓ All scripts check if columns already exist before adding them (idempotent)
✓ `sync_schema.py` requires confirmation before making changes
✓ Migrations only ADD columns, never DELETE (safe for production)
✓ All scripts work with both local and production databases via `DATABASE_URL`

## Future Schema Changes

When adding new columns to models:

1. Update the SQLAlchemy model in `database.py`
2. Create a migration script (copy `add_currency_column.py` as template)
3. Test locally first
4. Run on Render via shell or one-time job
5. Document the migration in this README

## Troubleshooting

**"DATABASE_URL environment variable not set"**
- Make sure you're running in an environment where DATABASE_URL is available
- For local development, it's set automatically by `database.py`
- For Render, it's set automatically in the environment

**"Permission denied"**
- Ensure the database user has ALTER TABLE permissions
- Render's default PostgreSQL user should have these permissions

**"Table does not exist"**
- Run `sync_schema.py` instead - it will create missing tables first

## Migration History

| Date | Script | Description |
|------|--------|-------------|
| 2025-11-28 | `add_currency_column.py` | Added `currency` column to `saved_budgets` table |
