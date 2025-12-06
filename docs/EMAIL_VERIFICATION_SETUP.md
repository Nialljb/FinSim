# Email Verification Setup Guide

## Overview

FinSim now includes email verification for new account registrations. Users must verify their email address before they can log in.

## Features

- ✅ Secure email verification with 24-hour expiring tokens
- ✅ HTML and plain text email templates
- ✅ Resend verification email option
- ✅ Welcome email after successful verification
- ✅ Beautiful branded email designs
- ✅ Automatic token invalidation after use

## User Flow

1. **Registration**: User creates account
2. **Verification Email**: System sends verification email with unique link
3. **Click Link**: User clicks verification link in email
4. **Verification**: System verifies token and activates account
5. **Welcome Email**: System sends welcome email
6. **Login**: User can now log in

## Email Configuration

### Environment Variables

Add these to your `.env` file or Render environment variables:

```bash
# Microsoft 365 / Office 365 (GoDaddy)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=niall@finstk.com
SMTP_PASSWORD=your-microsoft-365-password
SENDER_EMAIL=niall@finstk.com
SENDER_NAME=FinSim

# Application URL
BASE_URL=https://www.finstk.com
```

### Microsoft 365 Setup (Recommended - Your Current Setup)

1. **Use Your Microsoft 365 Credentials**
   - Email: `niall@finstk.com`
   - Password: Your Microsoft 365 account password
   - Server: `smtp.office365.com`
   - Port: `587` (TLS/STARTTLS)

2. **Verify SMTP is Enabled**
   - Sign in to Microsoft 365 admin center
   - Go to Settings > Mail
   - Ensure SMTP authentication is enabled

3. **Configure Environment**
   ```bash
   SMTP_SERVER=smtp.office365.com
   SMTP_PORT=587
   SMTP_USERNAME=niall@finstk.com
   SMTP_PASSWORD=your-password
   SENDER_EMAIL=niall@finstk.com
   SENDER_NAME=FinSim
   ```

4. **Security Best Practices**
   - Consider enabling 2FA on your Microsoft account
   - Use App Password if available in security settings
   - Monitor sent mail in your Sent Items folder

### Gmail Setup (Recommended for Testing)

1. **Enable 2-Step Verification**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Create new app password for "Mail"
   - Use the 16-character password as `SMTP_PASSWORD`

3. **Configure Environment**
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your.gmail@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # 16-char app password
   SENDER_EMAIL=your.gmail@gmail.com
   SENDER_NAME=FinSim
   ```

### Alternative SMTP Providers

#### SendGrid
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

#### Mailgun
```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@your-domain.mailgun.org
SMTP_PASSWORD=your-mailgun-password
```

#### AWS SES
```bash
SMTP_SERVER=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

## Database Migration

### Local Development (SQLite)

```bash
python migrate_email_verification.py
```

This creates the `email_verifications` table with:
- `id`: Primary key
- `user_id`: Foreign key to users table
- `email`: Email address being verified
- `token`: Unique verification token (SHA-256 hash)
- `is_used`: Whether token has been used
- `created_at`: Token creation timestamp
- `expires_at`: Token expiration (24 hours after creation)
- `verified_at`: When verification was completed

### Production (Render/PostgreSQL)

The migration runs automatically during deployment via `render-build-with-meta.sh`.

## Testing Email Verification

### Local Testing

1. **Set up SMTP credentials** in `.env`

2. **Run migration**:
   ```bash
   python migrate_email_verification.py
   ```

3. **Start Streamlit**:
   ```bash
   streamlit run wealth_simulator.py
   ```

4. **Register new account**:
   - Fill in registration form
   - Click "Create Account"
   - Check email for verification link

5. **Verify email**:
   - Click link in email
   - Should see success message
   - Can now log in

### Testing Without Email Server

For development without SMTP, you can manually verify users:

```python
from database import SessionLocal, User

db = SessionLocal()
user = db.query(User).filter(User.email == "test@example.com").first()
user.email_verified = True
db.commit()
db.close()
```

## Email Templates

### Verification Email

- **Subject**: "Verify Your FinSim Account"
- **Content**: Welcome message with verification button/link
- **Expiry**: 24 hours
- **Design**: Branded HTML with gradient header

### Welcome Email

- **Subject**: "Welcome to FinSim - Let's Get Started!"
- **Content**: Feature overview and getting started guide
- **Sent**: After successful email verification
- **Design**: Branded HTML with feature highlights

## Security Features

1. **Token Generation**
   - SHA-256 hashed tokens
   - Random 32-byte component
   - Timestamp-based uniqueness

2. **Expiration**
   - Tokens expire after 24 hours
   - Automatic invalidation after use
   - Old tokens invalidated when resending

3. **Privacy**
   - No email enumeration (generic messages)
   - Secure password hashing (bcrypt)
   - Email verification required before login

## User Interface

### Registration Tab
- Standard registration form
- Success message with email notification
- Balloon animation on success

### Login Tab
- Username/email + password
- Error message if email not verified
- Link to resend verification

### Resend Verification Tab
- Email input field
- Sends new verification email
- Invalidates old tokens

### Verification Page
- Auto-loads from URL parameter `?verify=TOKEN`
- Shows success/error message
- Provides resend option if expired

## Troubleshooting

### Email Not Sending

1. **Check SMTP credentials**:
   ```bash
   echo $SMTP_USERNAME
   echo $SMTP_PASSWORD
   ```

2. **Test SMTP connection**:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email', 'your-password')
   server.quit()
   ```

3. **Check Render logs** for error messages

### Verification Link Not Working

1. **Check BASE_URL** is set correctly
2. **Verify token in database** hasn't expired
3. **Check URL format**: `https://app.com/?verify=TOKEN`

### Gmail "Less Secure Apps" Error

Gmail no longer supports "less secure apps". You MUST use an App Password:
1. Enable 2-Step Verification
2. Create App Password
3. Use App Password as SMTP_PASSWORD

## Production Deployment (Render)

1. **Set Environment Variables** in Render dashboard:
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `SENDER_EMAIL`
   - `SENDER_NAME`
   - `BASE_URL=https://www.finstk.com`

2. **Deploy**:
   - Migration runs automatically
   - No downtime required

3. **Verify**:
   - Register test account
   - Check email delivery
   - Click verification link
   - Confirm login works

## Monitoring

Check these metrics:
- Email delivery success rate
- Token expiration rate
- Time to verification
- Resend requests

Query verification status:
```sql
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN is_used THEN 1 END) as verified,
    COUNT(CASE WHEN expires_at < NOW() THEN 1 END) as expired
FROM email_verifications;
```

## Future Enhancements

- [ ] Password reset via email
- [ ] Email change verification
- [ ] Email delivery tracking
- [ ] Rate limiting on resend
- [ ] Email templates customization
- [ ] Multi-language support
- [ ] SMS verification option

## Support

For issues with email verification:
1. Check Render logs
2. Verify SMTP credentials
3. Test with Gmail first
4. Open GitHub issue if problems persist
