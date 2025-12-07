# Database Schema Issue - Fix Guide

## The Problem

Your Render app is crashing with this error:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column saved_budgets.currency does not exist
```

## Why This Happened

1. **Your code (SQLAlchemy model)** expects a `currency` column in the `saved_budgets` table
2. **Your Render database** doesn't have this column yet
3. **Schema mismatch** = The database structure doesn't match your code

This is common when:
- You add new columns to your models locally
- You deploy the updated code to Render
- But the production database schema wasn't updated

## The Solution

### 🚀 Quick Fix (Recommended)

**Via Render Shell:**

1. Open your Render Dashboard
2. Navigate to your Web Service (finsim-app)
3. Click **"Shell"** in the left sidebar
4. Run this command:
   ```bash
   python fix_render_db.py
   ```
5. Wait for confirmation message: ✓ Successfully added 'currency' column!
6. Restart your service (optional - it auto-restarts)

**That's it!** Your app should work now.

### 🔧 Alternative Methods

**Method 2: Via Render's PostgreSQL Console**

1. Go to your database in Render Dashboard
2. Click "Query" or "Connect"
3. Run this SQL:
   ```sql
   ALTER TABLE saved_budgets ADD COLUMN currency VARCHAR(10) NULL;
   ```

**Method 3: Local Connection to Render DB**

If you have the database credentials:
```bash
export DATABASE_URL="postgresql://user:pass@host/db"
python fix_render_db.py
```

**Method 4: Comprehensive Schema Sync**

For fixing ALL schema mismatches (not just this one):
```bash
# In Render Shell
python migrations/sync_schema.py
```

This will:
- Check all tables
- Find all missing columns
- Show you what needs to be added
- Ask for confirmation
- Apply all migrations

## Verification

After running the fix:

1. Check the logs in Render Dashboard
2. Visit your app URL
3. You should see the app load without errors
4. Test the Budget Builder section (this is where the error occurred)

## Prevention for Future

**When you add new database columns:**

1. Update your model in `database.py` (you already do this)
2. Test locally (works because SQLAlchemy creates columns automatically on SQLite)
3. Deploy to Render
4. **RUN MIGRATION** - Don't forget this step!
5. Test on Render

**Best Practice:**
- Add migration scripts to your deployment process
- Or run `python migrations/sync_schema.py` after each deploy that changes models
- Document schema changes in `migrations/README.md`

## Files Created

I've created these files to help you:

1. **`fix_render_db.py`** - Quick one-command fix for this specific issue
2. **`migrations/add_currency_column.py`** - Standalone migration for currency column
3. **`migrations/sync_schema.py`** - Comprehensive schema sync tool
4. **`migrations/README.md`** - Full migration documentation

## Technical Details

**What the currency column is for:**
- Stores currency code (EUR, USD, GBP, etc.)
- Allows users to save budgets in different currencies
- Part of the Budget Builder feature

**Why it was added:**
- To support multi-currency budgeting
- Users in different countries use different currencies
- Integrates with your currency converter feature

**Schema definition:**
```python
currency = Column(String(10), nullable=True)  # Currency code (EUR, USD, etc.)
```

## Need Help?

If the fix doesn't work:

1. Check Render logs for detailed error messages
2. Verify DATABASE_URL is set in environment variables
3. Try the comprehensive sync: `python migrations/sync_schema.py`
4. Check that your database user has ALTER TABLE permissions
5. Review `migrations/README.md` for troubleshooting

## Summary

✅ **Run this in Render Shell:** `python fix_render_db.py`

That's all you need to do! The script is safe to run multiple times and will only add the column if it doesn't exist.
