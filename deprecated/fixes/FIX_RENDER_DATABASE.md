# 🚨 RENDER DATABASE FIX - READ THIS FIRST! 🚨

## If you're seeing database errors on Render, do this:

### Quick Fix (3 steps):

1. **Go to Render Dashboard** → Your FinSim Service → **Shell**
2. **Run this command:**
   ```bash
   python fix_render_all_migrations.py
   ```
3. **Wait for success messages** and refresh your app

That's it! This fixes all missing database columns.

---

## What errors does this fix?

✅ `column users.has_spouse does not exist`
✅ `column saved_budgets.current_month does not exist`
✅ `column saved_budgets.budget_expected does not exist`
✅ Any other "column does not exist" errors

## Why is this needed?

When you deploy code changes that add new database columns, the **code updates automatically** but the **database schema doesn't**. You need to manually run migrations to add the new columns to the production database.

## Is it safe?

✅ **100% safe** - Only adds missing columns, never deletes data
✅ **Idempotent** - Can run multiple times safely
✅ **Automatic checks** - Only adds columns that don't exist

## More details

See `/docs/FIX_RENDER_SPOUSE_ERROR.md` for comprehensive documentation.

---

**TL;DR:** Run `python fix_render_all_migrations.py` in Render Shell to fix database errors.
