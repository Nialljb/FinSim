# Auth0 Integration - Quick Reference

## Quick Start

### 1. Enable Auth0
```bash
# In .env file
ENABLE_AUTH0=True
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_secret
AUTH0_CALLBACK_URL=http://localhost:8501/
```

### 2. Run Database Migration
```bash
python scripts/migrations/add_auth0_column.py
```

### 3. Install Dependencies
```bash
pip install authlib python-jose[cryptography] requests
```

### 4. Test
```bash
streamlit run app/Home.py
```

## Files Modified/Created

### New Files
- `authentication/auth0_integration.py` - Auth0 OAuth client
- `scripts/migrations/add_auth0_column.py` - Database migration
- `scripts/admin/auth0_migration_helper.py` - User migration tools
- `docs/AUTH0_SETUP_GUIDE.md` - Comprehensive setup guide
- `.env.example` - Environment variable template

### Modified Files
- `requirements.txt` - Added Auth0 dependencies
- `config/settings.py` - Added Auth0 configuration
- `authentication/auth.py` - Added Auth0 helper functions
- `app/landing_page.py` - Added Auth0 login UI
- `data_layer/database.py` - Added auth0_id column to User model

## Key Features

### Dual Authentication
✅ Both Auth0 and traditional auth work simultaneously
✅ Existing users can continue with username/password
✅ New users can choose either method
✅ No data migration required immediately

### Security Improvements
✅ OAuth 2.0 / OpenID Connect standard
✅ No password storage for Auth0 users
✅ Built-in MFA support
✅ Social login (Google, Microsoft, Apple)
✅ Breach detection and anomaly protection

### User Experience
✅ One-click social login
✅ Faster registration
✅ Cross-device sessions
✅ Professional login UI
✅ No password to remember

## Configuration Options

### Minimal (Testing)
```bash
ENABLE_AUTH0=True
AUTH0_DOMAIN=dev-xyz.us.auth0.com
AUTH0_CLIENT_ID=abc123
AUTH0_CLIENT_SECRET=secret123
```

### Production
```bash
ENABLE_AUTH0=True
AUTH0_DOMAIN=prod-tenant.us.auth0.com
AUTH0_CLIENT_ID=prod_client_id
AUTH0_CLIENT_SECRET=prod_secret
AUTH0_CALLBACK_URL=https://yourdomain.com/
AUTH0_AUDIENCE=https://api.yourdomain.com  # Optional
```

### Disable Auth0
```bash
ENABLE_AUTH0=False
# All other Auth0 variables can be left empty
```

## Usage Examples

### Check Migration Status
```bash
python scripts/admin/auth0_migration_helper.py
```

### Test Auth0 Integration
```python
from authentication.auth0_integration import Auth0Client

client = Auth0Client()
auth_url, state = client.get_authorization_url()
print(f"Login URL: {auth_url}")
```

### Check if Auth0 is Enabled
```python
from authentication.auth import is_auth0_enabled

if is_auth0_enabled():
    print("Auth0 is active")
```

## Database Schema

### User Table (Updated)
```sql
ALTER TABLE users ADD COLUMN auth0_id VARCHAR(255) UNIQUE;
CREATE INDEX idx_users_auth0_id ON users(auth0_id);
```

### User Authentication Types
- **Traditional:** `auth0_id IS NULL` - username/password
- **Auth0:** `auth0_id IS NOT NULL` - OAuth user

## Auth0 Dashboard Quick Links

- **Applications:** Configure your app
- **Users:** View registered users
- **Logs:** Monitor authentication attempts
- **Security:** Enable MFA, breach detection
- **Branding:** Customize login page
- **Social:** Configure Google, Microsoft, etc.

## Troubleshooting

### Auth0 button not showing
```bash
# Check environment
echo $ENABLE_AUTH0  # Should be "True"

# Restart app
streamlit run app/Home.py
```

### "Invalid callback URL" error
- Verify callback URL in Auth0 matches exactly
- Include trailing slash if needed
- Check http vs https

### Users can't login
- Check Auth0 logs for specific error
- Verify social connection is enabled
- Ensure user's email is verified

### State parameter error
- Clear browser cookies
- Check session state is being stored
- Verify CSRF protection is working

## Cost Overview

| Tier | MAU | Cost/Month | Best For |
|------|-----|------------|----------|
| Free | 7,000 | $0 | Development, small apps |
| Essentials | 500-20K | $35+ | Growing apps |
| Professional | Unlimited | Custom | Enterprise |

**MAU = Monthly Active Users** (users who login at least once per month)

## Testing Checklist

- [ ] Auth0 button appears on login page
- [ ] Can click Auth0 button and redirects to Auth0
- [ ] Can login with Google/social provider
- [ ] User created in database with auth0_id
- [ ] Can logout and login again
- [ ] Traditional auth still works
- [ ] Existing users can still login
- [ ] Session persists across page reloads
- [ ] Callback URL handling works
- [ ] Error messages display correctly

## Deployment Checklist

- [ ] .env configured with production values
- [ ] Database migration completed
- [ ] Dependencies installed
- [ ] Auth0 application configured
- [ ] Callback URLs updated in Auth0
- [ ] Social connections enabled
- [ ] MFA configured (optional)
- [ ] Branding customized (optional)
- [ ] Monitoring/logs set up
- [ ] Rollback plan documented
- [ ] Team trained on new auth flow
- [ ] Users notified (if migration)

## Support

- **Setup Guide:** `docs/AUTH0_SETUP_GUIDE.md`
- **Migration:** `scripts/admin/auth0_migration_helper.py`
- **Issues:** GitHub Issues or support@finstk.com
- **Auth0 Docs:** https://auth0.com/docs

## Next Steps

1. **Testing Phase:**
   - Enable in development
   - Test all user flows
   - Verify existing users work

2. **Soft Launch:**
   - Enable for new users only
   - Monitor for issues
   - Collect feedback

3. **Full Rollout:**
   - Notify existing users
   - Offer Auth0 linking
   - Track adoption metrics

4. **Optimization:**
   - Customize branding
   - Enable MFA
   - Review security settings

---

**Version:** 1.0  
**Last Updated:** January 2026
