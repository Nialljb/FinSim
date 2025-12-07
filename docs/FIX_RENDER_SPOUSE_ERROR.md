# Fix Render Database Errors

## Errors You're Seeing

### Error 1: Missing spouse columns
```
Login failed: (psycopg2.errors.UndefinedColumn) column users.has_spouse does not exist
```

### Error 2: Missing budget tracking columns
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column saved_budgets.current_month does not exist
```

## Solution

The production database on Render is missing several columns that were added to the code. You need to run a comprehensive migration to add all missing columns.

## Steps to Fix (Use This Instead)

### Run Comprehensive Migration via Render Shell

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Select your FinSim web service

2. **Open Shell**
   - Click "Shell" in the left sidebar
   - Wait for the shell to connect

3. **Run the Comprehensive Migration**
   ```bash
   python fix_render_all_migrations.py
   ```

4. **Verify Success**
   - You should see output like:
     ```
     📋 Checking users table for spouse fields...
     ✅ Added users.has_spouse
     ✅ Added users.spouse_age
     ✅ Added users.spouse_retirement_age
     ✅ Added users.spouse_annual_income
     
     📋 Checking saved_budgets table for monthly tracking fields...
     ✅ Added saved_budgets.current_month
     ✅ Added saved_budgets.budget_expected
     ✅ Added saved_budgets.budget_actuals
     
     ✅ All migrations completed!
     ```

5. **Refresh Your App**
   - Try logging in and using the budget builder - it should work now!

### Option 2: Via Local Connection (If you have DB credentials)

If you have access to the Render PostgreSQL database credentials:

1. **Get Database URL**
   - In Render dashboard, go to your database
   - Copy the "External Database URL"

2. **Set Environment Variable**
   ```bash
   export DATABASE_URL="your_postgresql_url_here"
   ```

3. **Run Migration**
   ```bash
   python fix_render_spouse_fields.py
   ```

### Option 3: Automatic on Next Deploy

Add this to your `initiate.sh` or deployment script:

```bash
# Run spouse fields migration
python fix_render_spouse_fields.py || true
```

This will automatically run the migration on every deployment (safe because it checks for existing columns).

## What This Migration Does

The script adds all missing columns to your production database:

**users table:**
- `has_spouse` (BOOLEAN) - Whether user has a spouse/partner
- `spouse_age` (INTEGER) - Spouse's age
- `spouse_retirement_age` (INTEGER) - Spouse's retirement age
- `spouse_annual_income` (FLOAT) - Spouse's annual income in base currency

**saved_budgets table:**
- `current_month` (VARCHAR) - Current month being tracked (format: "2025-12")
- `budget_expected` (JSON) - Expected monthly budget by category
- `budget_actuals` (JSON) - Actual spending by month and category

**feedback table:**
- Makes `user_id` nullable to allow anonymous submissions

**pension_plans table** (if it exists):
- 26 spouse-related pension fields for State Pension, USS, SIPP, and AVCs

## Safety

✅ **Safe to run multiple times** - Checks if columns exist before adding
✅ **No data loss** - Only adds columns, never removes or modifies existing data
✅ **Automatic rollback** - If any error occurs, no partial changes are made
✅ **Production tested** - Works with PostgreSQL (Render's database)

## Troubleshooting

**"DATABASE_URL environment variable not set"**
- This is set automatically in Render Shell, so use Option 1

**"Permission denied"**
- Render's default PostgreSQL user has necessary permissions
- If you see this, contact Render support

**Still getting errors after migration?**
- Make sure you ran the migration successfully (saw ✅ messages)
- Try restarting your Render service
- Check the Render logs for other errors

## Future Deployments

To avoid this issue in the future:

1. **Before deploying code with new database columns:**
   - Create a migration script (use `fix_render_spouse_fields.py` as template)
   - Test locally first
   - Run on Render before or immediately after deployment

2. **Consider automating migrations:**
   - Add migration runner to `initiate.sh`
   - Or use a database migration tool like Alembic

## Need Help?

If you continue to have issues:
1. Check the full error message in Render logs
2. Verify the migration ran successfully (check output)
3. Ensure you're running the latest deployed code
4. Try a hard refresh/restart of the Render service
