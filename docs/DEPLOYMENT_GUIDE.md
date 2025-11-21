# 🚀 Production Deployment Guide

## Option A: Render (Recommended to Start)

### ✅ Why Render?

- ✅ Familiar platform for you
- ✅ Free PostgreSQL database included
- ✅ Auto-deploy from GitHub
- ✅ HTTPS included
- ✅ Zero config needed
- ✅ Can be live in 30 minutes

### 📋 Prerequisites

1. GitHub account with your code
2. Render account (free): https://render.com
3. Clean up your code for production

### 🔧 Step 1: Prepare Your Code

**Create these files in your project root:**

#### 1. `render.yaml` (already created for you)
```yaml
services:
  - type: web
    name: finsim-app
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run wealth_simulator.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: finsim-db
          property: connectionString

databases:
  - name: finsim-db
    plan: starter
    databaseName: finsim
```

#### 2. `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Database
*.db
*.db-journal
finsim.db

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml
```

#### 3. `runtime.txt` (optional)
```
python-3.11.0
```

#### 4. Update `requirements.txt`
Make sure it has everything:
```
streamlit>=1.28.0
numpy>=1.24.0
pandas>=2.0.0
plotly>=5.17.0
xlsxwriter>=3.1.0
reportlab>=4.0.0
kaleido>=0.2.1
sqlalchemy>=2.0.0
bcrypt>=4.0.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.0
```

### 🚀 Step 2: Deploy to Render

**Method 1: Blueprint (Easiest)**

1. Push your code to GitHub
2. Go to https://dashboard.render.com
3. Click "New" → "Blueprint"
4. Connect your GitHub repo
5. Render reads `render.yaml` automatically
6. Click "Apply"
7. Wait 5-10 minutes for deployment

**Method 2: Manual Setup**

1. **Create Database:**
   - Dashboard → New → PostgreSQL
   - Name: `finsim-db`
   - Plan: Free or Starter ($7/mo)
   - Click "Create Database"
   - Copy the "Internal Database URL"

2. **Create Web Service:**
   - Dashboard → New → Web Service
   - Connect GitHub repo
   - Name: `finsim-app`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run wealth_simulator.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
   - Plan: Starter ($7/mo) or Free (with sleep)

3. **Add Environment Variables:**
   - DATABASE_URL: (paste from step 1)
   - SECRET_KEY: (generate random: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - FREE_SIMULATION_LIMIT: `5`

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for build & deploy (5-10 min)

### 🔧 Step 3: Initialize Database

After deployment, run setup once:

```bash
# Option 1: Use Render Shell
# In Render dashboard, go to your web service → Shell tab
python setup.py

# Option 2: Add to build command (one-time)
pip install -r requirements.txt && python setup.py
```

### 🌐 Step 4: Custom Domain (Optional)

1. Go to your Render service
2. Settings → Custom Domains
3. Add: `finsim.yourdomain.com`
4. Update DNS:
   - Type: CNAME
   - Name: finsim
   - Value: (from Render)
5. Wait for SSL (automatic, 5-10 min)

### 📊 Step 5: Monitor & Scale

**Free Tier Limits:**
- Database: 1GB storage, 100 connections
- Web: Spins down after 15 min inactivity
- Builds: 500 hours/month

**When to Upgrade ($7/mo Starter):**
- ✅ No auto-sleep
- ✅ Better performance
- ✅ 10GB database
- ✅ Recommended once you have 10+ active users

### 🔒 Step 6: Production Checklist

- [ ] Remove test user (or change password)
- [ ] Set strong SECRET_KEY
- [ ] Enable database backups in Render
- [ ] Set up monitoring (Render has built-in)
- [ ] Test all flows (register, login, simulate, export)
- [ ] Update landing page with real domain
- [ ] Add analytics (optional: Google Analytics in Streamlit)

---

## 🎨 Enhanced Landing Page

I've created a professional landing page with:
- ✅ Hero section with value proposition
- ✅ Social proof stats
- ✅ Login & registration forms
- ✅ Feature showcase
- ✅ How it works section
- ✅ Testimonials
- ✅ Professional styling

**To use:**

1. Copy `landing_page.py` to your project
2. Import the function: `from landing_page import show_landing_page`
3. Replace your login check:

```python
# OLD:
if not st.session_state.get('authenticated', False):
    show_login_page()
    st.stop()

# NEW:
if not st.session_state.get('authenticated', False):
    show_landing_page()
    st.stop()
```

---

## 🔄 Update & Redeploy

Render auto-deploys on git push:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render automatically rebuilds (takes 3-5 min)
```

---

## 📈 Option B: Fly.io (Future Migration)

When you outgrow Render (100+ concurrent users):

**Advantages:**
- Faster (edge deployment)
- Cheaper at scale
- Better performance
- Global regions

**Setup:**
1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "wealth_simulator.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Deploy:
```bash
fly launch
fly deploy
```

**Cost Comparison:**

| Service | Free Tier | Paid |
|---------|-----------|------|
| Render | Yes (sleeps) | $7/mo |
| Fly.io | 3 VMs free | ~$5/mo |

**Recommendation:** Start with Render, migrate to Fly.io at ~$100-200/month traffic.

---

## 🎯 Your Launch Timeline

**Week 1 (Now):**
- [ ] Push code to GitHub
- [ ] Deploy to Render (free tier)
- [ ] Add landing page
- [ ] Test thoroughly
- [ ] Share with 5 beta users

**Week 2:**
- [ ] Collect feedback
- [ ] Fix bugs
- [ ] Upgrade to Render Starter ($7/mo)
- [ ] Add custom domain
- [ ] Soft launch (share with friends/colleagues)

**Month 2:**
- [ ] Monitor usage
- [ ] Gather user data
- [ ] Add analytics
- [ ] Consider monetization

**Month 6+:**
- [ ] If growing: migrate to Fly.io
- [ ] If not: stay on Render (it's great!)

---

## 🆘 Troubleshooting

**Build fails:**
```bash
# Check requirements.txt has all dependencies
# Make sure Python version matches (3.11)
# Check logs in Render dashboard
```

**Database connection fails:**
```bash
# Verify DATABASE_URL is set
# Check database is running
# Try: pip install psycopg2-binary
```

**App is slow:**
```bash
# Upgrade from free tier
# Enable caching in Streamlit
# Optimize queries
```

**Authentication issues:**
```bash
# Run setup.py to create tables
# Check SECRET_KEY is set
# Verify database has user table
```

---

## 📞 Next Steps

1. **Deploy NOW** - Use the Render blueprint method
2. **Test with real users** - Invite 5-10 people
3. **Iterate quickly** - Fix bugs, add features
4. **Monitor growth** - Watch Render metrics
5. **Scale when ready** - Upgrade plan or migrate

You can be live in production in the next hour! 🚀
