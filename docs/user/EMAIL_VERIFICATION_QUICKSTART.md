# Email Verification - Quick Start

## What Was Added

✅ **Email verification system** for new user registrations
✅ **Beautiful HTML email templates** with branding
✅ **24-hour expiring verification tokens**
✅ **Resend verification option**
✅ **Welcome email after verification**
✅ **Database migration scripts**

## Files Created/Modified

### New Files
- `email_service.py` - Email sending and template generation
- `migrate_email_verification.py` - Database migration script
- `.env.example` - Environment variable template
- `docs/EMAIL_VERIFICATION_SETUP.md` - Full documentation

### Modified Files
- `auth.py` - Added verification functions and UI
- `database.py` - Added EmailVerification table
- `render-build-with-meta.sh` - Added migration to build script

## Quick Setup

### 1. Run Migration (Local)
```bash
python migrate_email_verification.py
```

### 2. Configure Email (Development)

Create `.env` file:
```bash
# Microsoft 365 via GoDaddy
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=niall@finstk.com
SMTP_PASSWORD=your-password-here
SENDER_EMAIL=niall@finstk.com
SENDER_NAME=FinSim
BASE_URL=http://localhost:8501
```

**Microsoft 365 Setup:**
1. Use your full email: `niall@finstk.com`
2. Use your Microsoft 365 account password
3. Ensure SMTP is enabled in Microsoft 365 admin panel
4. Server: `smtp.office365.com`, Port: `587`

**Alternative - Gmail (for testing):**
**Alternative - Gmail (for testing):**
1. https://myaccount.google.com/security → Enable 2FA
2. https://myaccount.google.com/apppasswords → Create "Mail" password
3. Use 16-character password in `.env`

### 3. Test Locally
```bash
streamlit run wealth_simulator.py
```

1. Click "Register" tab
2. Create account
3. Check email for verification link
4. Click link
5. Login with verified account

## Production Setup (Render)

### Add Environment Variables in Render Dashboard:
```
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=niall@finstk.com
SMTP_PASSWORD=your-microsoft-365-password
SENDER_EMAIL=niall@finstk.com
SENDER_NAME=FinSim
BASE_URL=https://www.finstk.com
```

### Deploy:
```bash
git add .
git commit -m "Add email verification"
git push origin email_verification
```

Migration runs automatically during build!

## User Experience

### Registration Flow
1. User fills registration form
2. Sees success message: "Check your email!"
3. Receives branded verification email
4. Clicks verification link
5. Sees "Email verified!" with balloons 🎉
6. Receives welcome email
7. Can now login

### If Email Not Verified
- Login shows: "Please verify your email before logging in"
- User can use "Resend Verification" tab
- New link sent, old tokens invalidated

## Email Templates

### Verification Email
- Subject: "Verify Your FinSim Account"
- Gradient purple header
- Big verification button
- 24-hour expiry notice

### Welcome Email  
- Subject: "Welcome to FinSim - Let's Get Started!"
- Feature highlights
- Getting started button
- Support information

## Testing Without Email

For development without SMTP setup:

```python
from database import SessionLocal, User

db = SessionLocal()
user = db.query(User).filter(User.email == "test@example.com").first()
user.email_verified = True
db.commit()
```

## Troubleshooting

**Emails not sending?**
- Check SMTP credentials in `.env`
- Verify Gmail App Password (not regular password)
- Check spam folder

**Verification link not working?**
- Check BASE_URL is correct
- Token expires in 24 hours
- Use "Resend Verification" tab

**Migration failed?**
- Already ran? Table exists, skip error
- PostgreSQL: Runs automatically on Render
- SQLite: Run `python migrate_email_verification.py`

## Next Steps

See `docs/EMAIL_VERIFICATION_SETUP.md` for:
- Alternative SMTP providers (SendGrid, Mailgun, AWS SES)
- Security details
- Monitoring queries
- Email customization
- Future enhancements

## Support

Questions? Check:
1. Full docs: `docs/EMAIL_VERIFICATION_SETUP.md`
2. Environment: `.env.example`
3. GitHub Issues: Report bugs/requests
