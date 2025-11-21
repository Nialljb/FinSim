# Render Pricing Reference (Updated 2024)

## 🗄️ Database Plans

| Plan | Price | Storage | Notes |
|------|-------|---------|-------|
| **free** | $0 | 1 GB | Expires after 90 days of inactivity |
| **standard** | $7/mo | 10 GB | No expiration, daily backups |
| **pro** | $25/mo | 50 GB | Enhanced performance |
| **pro plus** | $90/mo | 100 GB | Maximum performance |

## 🌐 Web Service Plans

| Plan | Price | Notes |
|------|-------|-------|
| **free** | $0 | Spins down after 15 min inactivity (wakes in ~30 sec) |
| **starter** | $7/mo | No sleep, 512 MB RAM, 0.5 CPU |
| **standard** | $25/mo | 2 GB RAM, 1 CPU |
| **pro** | $85/mo | 4 GB RAM, 2 CPU |

## 💡 Recommended Configurations

### Option 1: Completely Free (Testing)
```yaml
services:
  - type: web
    plan: free  # Sleeps after 15 min
databases:
  - plan: free  # 1GB, expires after 90 days
```
**Total: $0/month**
**Good for:** Testing, demos, personal use

### Option 2: Always On (Production)
```yaml
services:
  - type: web
    plan: starter  # $7, no sleep
databases:
  - plan: standard  # $7, 10GB
```
**Total: $14/month**
**Good for:** 100-500 users, production app

### Option 3: Budget Hybrid (Recommended to Start)
```yaml
services:
  - type: web
    plan: starter  # $7, no sleep
databases:
  - plan: free  # $0, 1GB
```
**Total: $7/month**
**Good for:** Early users, validate product
**Note:** Upgrade database to 'standard' when you hit 500MB or 90 days

## 📊 When to Upgrade

**Start with:** Free web + Free database ($0)
- Test with friends
- Validate concept
- Up to 10 beta users

**Upgrade to:** Starter web + Free database ($7/mo)
- When you share publicly
- No more sleep delays
- Up to 100 users

**Upgrade to:** Starter web + Standard database ($14/mo)
- When database > 500MB
- After 90 days
- 100-500 active users
- Need backups

**Upgrade to:** Standard web + Standard database ($32/mo)
- 500+ active users
- Complex simulations
- High traffic

## 🎯 Your Launch Path

**Month 1:** Free ($0)
- Testing & validation
- 10 beta users

**Month 2:** Starter + Free ($7)
- Soft launch
- 50 users

**Month 3:** Starter + Standard ($14)
- Public launch
- 200 users

**Month 6+:** Standard + Standard ($32)
- Growing userbase
- 1000+ users

## 🆓 Database Free Tier Notes

- **Storage:** 1 GB (plenty for 1000+ users with your schema)
- **Expiration:** 90 days of zero connections
- **Resets:** Any connection resets the 90-day timer
- **Upgrade:** Can upgrade to 'standard' anytime without data loss

**Your current schema estimate:**
- User: ~200 bytes/user
- Simulation: ~500 bytes/simulation
- UsageStats: ~100 bytes/user

**Capacity:**
- ~5000 users with 5 simulations each = ~15 MB
- You can run for months on free database!

## 💳 Billing Tips

1. **Start free** - Test everything
2. **Upgrade web first** ($7) - Better UX, no sleep
3. **Keep free database** - Until you hit limits
4. **Monitor usage** - Render dashboard shows metrics
5. **Upgrade gradually** - Only when needed

## 🔄 How to Change Plans

**In render.yaml:**
```yaml
databases:
  - plan: free  # Change to 'standard' when ready
```

**Or in Render Dashboard:**
1. Go to database
2. Settings → Plan
3. Select new plan
4. Confirm (prorated billing)

## 📈 Cost Projections

| Users | Simulations/Month | Est. Data | Recommended Plan | Cost |
|-------|-------------------|-----------|------------------|------|
| 10 | 50 | 1 MB | Free + Free | $0 |
| 100 | 500 | 10 MB | Starter + Free | $7 |
| 500 | 2,500 | 50 MB | Starter + Standard | $14 |
| 1,000 | 5,000 | 100 MB | Standard + Standard | $32 |
| 5,000 | 25,000 | 500 MB | Standard + Standard | $32 |

Your schema is very efficient - you can support thousands of users on the $14/month plan!
