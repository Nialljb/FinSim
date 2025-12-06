# Quick Fix Guide - Render Database Error

## ⚡ The Error You're Seeing

```
column saved_budgets.currency does not exist
```

## ⚡ The Fix (30 seconds)

### On Render Dashboard:

1. Click your web service → **"Shell"**
2. Run:
   ```bash
   python fix_render_db.py
   ```
3. Done! ✅

### Expected Output:
```
Using database URL from config
Connecting to database...
Adding 'currency' column to saved_budgets table...
✓ Successfully added 'currency' column!

Done! The app should now work correctly.
```

## Alternative: SQL Console

If Shell doesn't work, use the PostgreSQL Query console:

```sql
ALTER TABLE saved_budgets ADD COLUMN currency VARCHAR(10) NULL;
```

## What This Does

- Adds the missing `currency` column to your database
- Safe to run multiple times (checks if column exists first)
- No data loss
- Immediate fix

## Files Reference

- **Quick fix:** `fix_render_db.py`
- **Full guide:** `DATABASE_FIX.md`
- **Migration docs:** `migrations/README.md`

---

**Need more help?** See `DATABASE_FIX.md` for detailed instructions and troubleshooting.
