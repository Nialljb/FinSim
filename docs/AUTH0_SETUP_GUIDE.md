# Auth0 Integration Setup Guide for FinSim

## Overview

This guide walks you through setting up Auth0 authentication for FinSim, enabling secure OAuth2-based login with support for Google, Microsoft, Apple, and other identity providers.

## Benefits of Auth0 Integration

### Security
- ✅ No password storage - reduces breach risk
- ✅ Industry-standard OAuth 2.0 / OpenID Connect
- ✅ Built-in MFA (multi-factor authentication)
- ✅ Anomaly detection and breach prevention
- ✅ Compliance-ready (GDPR, SOC2, HIPAA)

### User Experience
- ✅ One-click social login (Google, Microsoft, Apple)
- ✅ No password to remember
- ✅ Faster registration process
- ✅ Cross-device session management
- ✅ Professional login UI

### Development
- ✅ Reduced authentication code maintenance
- ✅ Automatic security updates
- ✅ Simplified password reset flows
- ✅ Better audit logs and analytics

## Prerequisites

- Auth0 account (free tier: 7,000 MAU)
- Access to your application's environment variables
- Database with auth0_id column (migration script provided)

## Step 1: Create Auth0 Application

### 1.1 Sign Up for Auth0
1. Go to [auth0.com](https://auth0.com)
2. Click "Sign Up" and create an account
3. Choose your tenant domain (e.g., `finsim-prod.us.auth0.com`)

### 1.2 Create Application
1. In Auth0 Dashboard, go to **Applications** > **Applications**
2. Click **Create Application**
3. Name: `FinSim` (or your app name)
4. Type: Select **Regular Web Application**
5. Click **Create**

### 1.3 Configure Application Settings
In your application settings, configure:

**Allowed Callback URLs:**
```
http://localhost:8501,
http://localhost:8501/,
https://yourdomain.com,
https://yourdomain.com/
```

**Allowed Logout URLs:**
```
http://localhost:8501,
https://yourdomain.com
```

**Allowed Web Origins:**
```
http://localhost:8501,
https://yourdomain.com
```

### 1.4 Get Credentials
From the application settings, note:
- **Domain** (e.g., `finsim-prod.us.auth0.com`)
- **Client ID** (e.g., `abc123xyz...`)
- **Client Secret** (click "Show" to reveal)

## Step 2: Configure Social Connections (Optional)

Enable social login providers:

### 2.1 Google
1. Go to **Authentication** > **Social**
2. Find **Google** and toggle it on
3. Choose between:
   - Auth0 Dev Keys (for testing only)
   - Your own Google OAuth credentials (recommended for production)

### 2.2 Microsoft
1. Find **Microsoft Account** in Social connections
2. Toggle on and configure

### 2.3 Apple
1. Find **Apple** in Social connections
2. Configure Apple Sign In credentials

## Step 3: Configure Your Application

### 3.1 Update Environment Variables

Add to your `.env` file:

```bash
# Auth0 Configuration
ENABLE_AUTH0=True
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=your_client_id_here
AUTH0_CLIENT_SECRET=your_client_secret_here
AUTH0_CALLBACK_URL=http://localhost:8501/
# Optional: for API access
AUTH0_AUDIENCE=
```

**For Production:**
```bash
ENABLE_AUTH0=True
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_CLIENT_ID=your_prod_client_id
AUTH0_CLIENT_SECRET=your_prod_client_secret
AUTH0_CALLBACK_URL=https://yourdomain.com/
```

### 3.2 Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `authlib>=1.3.0` - OAuth client library
- `python-jose[cryptography]>=3.3.0` - JWT token verification
- `requests>=2.31.0` - HTTP requests

## Step 4: Database Migration

### 4.1 Add auth0_id Column

Run the migration script:

```bash
python scripts/migrations/add_auth0_column.py
```

This adds the `auth0_id` column to your users table and creates necessary indexes.

### 4.2 Verify Migration

The script will output:
```
✓ Successfully added auth0_id column
✓ Column exists: auth0_id (character varying)
```

## Step 5: Testing

### 5.1 Local Testing

1. Start your application:
   ```bash
   streamlit run app/Home.py
   ```

2. Navigate to the login page
3. You should see "🔐 Sign in with Auth0" button
4. Click it and test the OAuth flow

### 5.2 Test User Flow

1. **New User Registration:**
   - Click Auth0 button
   - Choose social provider (Google, etc.)
   - Authorize the application
   - User created with `auth0_id`

2. **Existing Auth0 User:**
   - Click Auth0 button
   - Sign in with same provider
   - Should login immediately

3. **Traditional Auth (Backward Compatibility):**
   - Enter username/password
   - Should still work for existing users

## Step 6: User Migration Strategy

### Option 1: Dual Authentication (Recommended)
Keep both Auth0 and traditional auth:
- Existing users continue with username/password
- New users can choose either method
- Gradual migration over time

### Option 2: Active Migration
Prompt existing users to link Auth0:
- Add "Link Auth0 Account" in settings
- Send migration emails
- Offer incentives

### Option 3: View Migration Status

```bash
python scripts/admin/auth0_migration_helper.py
```

This shows:
- Number of Auth0 vs traditional users
- Recent traditional auth users
- Migration email template
- Step-by-step migration plan

## Step 7: Production Deployment

### 7.1 Update Render/Production Environment

Add environment variables in your hosting platform:

**Render.com:**
1. Go to your service dashboard
2. Navigate to **Environment**
3. Add:
   ```
   ENABLE_AUTH0=True
   AUTH0_DOMAIN=your-tenant.us.auth0.com
   AUTH0_CLIENT_ID=your_prod_client_id
   AUTH0_CLIENT_SECRET=your_prod_client_secret
   AUTH0_CALLBACK_URL=https://yourapp.onrender.com/
   ```

### 7.2 Update Auth0 Callback URLs

In Auth0 Dashboard, update **Allowed Callback URLs** to include:
```
https://yourapp.onrender.com,
https://yourapp.onrender.com/
```

### 7.3 Deploy

```bash
git add .
git commit -m "Add Auth0 authentication integration"
git push origin main
```

## Step 8: Monitoring and Maintenance

### 8.1 Auth0 Dashboard Monitoring

Monitor in Auth0 Dashboard:
- **Logs** - View all authentication attempts
- **Users** - Manage user accounts
- **Anomaly Detection** - Security alerts
- **Analytics** - Login trends

### 8.2 Application Monitoring

Track metrics:
- Auth0 adoption rate
- Login success rate
- Traditional auth usage
- Support tickets related to auth

### 8.3 Security Best Practices

1. **Rotate Secrets Regularly**
   - Update `AUTH0_CLIENT_SECRET` every 90 days
   - Use Auth0's secret rotation feature

2. **Enable MFA**
   - Go to **Security** > **Multi-factor Auth**
   - Enable for all users or specific groups

3. **Configure Attack Protection**
   - Enable breached password detection
   - Configure suspicious IP throttling
   - Set up brute force protection

4. **Review Logs**
   - Check Auth0 logs weekly
   - Set up alerts for failed logins
   - Monitor for unusual patterns

## Troubleshooting

### Issue: "Auth0 configuration not properly set"

**Solution:**
- Verify all environment variables are set
- Check `AUTH0_DOMAIN` doesn't include `https://`
- Restart the application after updating `.env`

### Issue: "Invalid callback URL"

**Solution:**
- Verify callback URL in Auth0 matches exactly
- Include trailing slash if needed
- Check for http vs https mismatch

### Issue: "Invalid state parameter"

**Solution:**
- Clear browser cookies and try again
- This is CSRF protection - ensure state is being stored
- Check session state persistence

### Issue: Users can't find Auth0 button

**Solution:**
- Verify `ENABLE_AUTH0=True` in environment
- Check for errors in application logs
- Ensure dependencies are installed

## Advanced Configuration

### Custom Login Page

Auth0 allows customizing the login UI:
1. Go to **Branding** > **Universal Login**
2. Customize colors, logo, fonts
3. Match your FinSim branding

### Custom User Metadata

Store additional user data:
```python
# In auth0_integration.py, add custom metadata
user_metadata = {
    'preferred_currency': 'USD',
    'country': 'US'
}
```

### Rules and Actions

Add custom logic during authentication:
1. Go to **Auth Pipeline** > **Rules**
2. Create rules for:
   - Email domain whitelisting
   - Custom claims in tokens
   - Third-party enrichment

## Cost Estimates

### Auth0 Free Tier
- **Monthly Active Users:** 7,000 MAU
- **Cost:** $0
- **Good for:** Development, small apps

### Auth0 Essentials
- **Monthly Active Users:** 500-20,000 MAU
- **Cost:** Starting at $35/month
- **Features:** 
  - Social connections
  - MFA
  - Anomaly detection
  - 24/7 support

### Cost Optimization
- Monitor MAU usage monthly
- Consider user activity patterns
- Use both Auth0 and traditional auth

## Support and Resources

### Documentation
- [Auth0 Python Quickstart](https://auth0.com/docs/quickstart/webapp/python)
- [OAuth 2.0 Flow](https://auth0.com/docs/flows/authorization-code-flow)
- [Auth0 Management API](https://auth0.com/docs/api/management/v2)

### FinSim-Specific
- Migration helper: `scripts/admin/auth0_migration_helper.py`
- Database migration: `scripts/migrations/add_auth0_column.py`
- Auth0 integration: `authentication/auth0_integration.py`

### Community
- Auth0 Community Forums
- FinSim GitHub Issues
- Email: support@finstk.com

## Rollback Plan

If you need to disable Auth0:

1. **Update Environment:**
   ```bash
   ENABLE_AUTH0=False
   ```

2. **Restart Application:**
   ```bash
   # Application will revert to traditional auth only
   ```

3. **Users Affected:**
   - Auth0-only users will need password reset
   - Traditional auth users unaffected

4. **Data Preservation:**
   - All user data remains intact
   - `auth0_id` column preserved for re-enabling

## Conclusion

You've successfully integrated Auth0 into FinSim! Your users can now enjoy:
- ✅ Secure OAuth2 authentication
- ✅ Social login options
- ✅ Better security with MFA
- ✅ Improved user experience

For questions or issues, contact: support@finstk.com

---

**Last Updated:** January 2026  
**Version:** 1.0  
**Maintainer:** FinSim Development Team
