# Fixing PDF Export on Render

## Problem
PDF export works locally but shows "⚠️ PDF unavailable - use Excel export" when deployed on Render.

## Root Cause
The PDF export requires **Kaleido** to convert Plotly charts to images. Kaleido has known issues in containerized environments like Render because:

1. **Missing system dependencies**: Kaleido needs Chrome/Chromium libraries
2. **Security vulnerabilities**: Older Kaleido versions contain known CVEs
3. **Compatibility**: Requires specific system libraries in containerized environments

## Current Solution (Updated December 2024)

**Kaleido Version**: `kaleido==1.2.0` (upgraded from 0.2.1.post1 to address CVE vulnerabilities)

### Testing & Compatibility
- ✅ Local tests pass (test_pdf_export.py)
- ✅ Plotly chart conversion working (PNG, JPG, SVG formats)
- ✅ ReportLab PDF generation working
- ✅ wealth_simulator.py PDF_EXPORT_AVAILABLE check passes

### System Dependencies
The `render-build.sh` script installs required Chrome/Chromium libraries:

```txt
kaleido==1.2.0
```

### Option 2: Install System Dependencies on Render
Add a `render-build.sh` script to install required system packages:

```bash
#!/bin/bash
# Install Chrome dependencies for Kaleido
apt-get update
apt-get install -y \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0
```

Then update `render.yaml`:

```yaml
services:
  - type: web
    name: finsim
    env: python
    buildCommand: "./render-build.sh && pip install -r requirements.txt"
    startCommand: "streamlit run wealth_simulator.py --server.port=$PORT --server.address=0.0.0.0"
```

### Option 3: Switch to Alternative PDF Library
Replace Kaleido with **matplotlib + img2pdf** for more reliable deployment:

**Update requirements.txt:**
```txt
matplotlib>=3.7.0
Pillow>=10.0.0
img2pdf>=0.4.4
```

**Modify PDF export code to use matplotlib instead of Kaleido for chart rendering**

### Option 4: Use Serverless PDF Generation (Most Reliable)
Integrate with an external API like:
- **Plotly Chart Studio** (requires API key)
- **Imgkit/wkhtmltopdf** (more reliable than Kaleido)
- **Puppeteer/Playwright** (via separate service)

## Quick Fix for Production (Immediate)

### Step 1: Update requirements.txt
Change:
```txt
kaleido>=0.2.1
```
To:
```txt
kaleido==0.2.1.post1
```

### Step 2: Create render-build.sh in project root
```bash
#!/bin/bash
set -e

echo "Installing system dependencies for Kaleido..."

# Update package list
apt-get update -qq

# Install Chrome dependencies
apt-get install -y -qq \
    libx11-6 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libnss3 \
    libnspr4 \
    libglib2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libasound2 \
    libdbus-1-3 \
    libexpat1 \
    libuuid1

echo "System dependencies installed successfully"
echo "Installing Python packages..."
pip install -r requirements.txt

echo "Build complete!"
```

### Step 3: Make the script executable
```bash
chmod +x render-build.sh
```

### Step 4: Update render.yaml
```yaml
services:
  - type: web
    name: finsim
    env: python
    region: frankfurt
    plan: free
    buildCommand: "./render-build.sh"
    startCommand: "streamlit run wealth_simulator.py --server.port=$PORT --server.address=0.0.0.0"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: finsim-db
          property: connectionString
```

### Step 5: Test locally with Docker (Optional)
```bash
# Create Dockerfile for testing
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libx11-6 libx11-xcb1 libxcomposite1 libxcursor1 \
    libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 \
    libxrender1 libxss1 libxtst6 libnss3 libnspr4 \
    libglib2.0-0 libgdk-pixbuf2.0-0 libgtk-3-0 \
    libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0 \
    libcairo2 libfontconfig1 libfreetype6 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["streamlit", "run", "wealth_simulator.py"]
```

```bash
# Build and test
docker build -t finsim-test .
docker run -p 8501:8501 finsim-test
```

## Alternative: Disable PDF, Keep Excel Only

If the above doesn't work, you can gracefully disable PDF on production:

**Add to wealth_simulator.py (around line 80):**
```python
# Check PDF export availability
import os
DEPLOYMENT_ENV = os.getenv('RENDER', 'false')

if DEPLOYMENT_ENV == 'true':
    # Disable PDF on Render due to Kaleido issues
    PDF_EXPORT_AVAILABLE = False
    print("PDF export disabled on Render deployment")
else:
    try:
        import plotly.io as pio
        test_fig = go.Figure()
        pio.to_image(test_fig, format='png', width=10, height=10)
        PDF_EXPORT_AVAILABLE = True
    except Exception as e:
        PDF_EXPORT_AVAILABLE = False
        print(f"PDF export unavailable: {e}")
```

**Add to render.yaml:**
```yaml
envVars:
  - key: RENDER
    value: "true"
```

## Recommended Approach

**For immediate production deployment:**
1. Use Option 4 (Disable PDF on production, keep Excel)
2. Add helpful message explaining Excel export has all the same data

**For long-term solution:**
1. Implement Option 1 + Option 2 (Updated Kaleido + system deps)
2. Test thoroughly on Render
3. If still issues, switch to Option 3 (matplotlib-based PDF generation)

## Testing Checklist

After implementing the fix:

- [ ] Deploy to Render
- [ ] Log into the app
- [ ] Run a simulation
- [ ] Click "📄 Export to PDF" button
- [ ] Check button is enabled (not grayed out)
- [ ] Download completes successfully
- [ ] Open PDF and verify:
  - [ ] Charts render correctly
  - [ ] Tables are formatted
  - [ ] All data is present
  - [ ] Currency symbols display correctly

## Troubleshooting

If PDF export still fails after implementation:

1. **Check Render logs** for Kaleido errors
2. **Verify system packages installed** in build logs
3. **Test Kaleido directly** in Render shell:
   ```python
   import plotly.graph_objects as go
   import plotly.io as pio
   fig = go.Figure()
   pio.to_image(fig, format='png')
   ```
4. **Check Render's Python version** matches local (3.11+)
5. **Verify file permissions** on render-build.sh

## Support Resources

- [Kaleido GitHub Issues](https://github.com/plotly/Kaleido/issues)
- [Render Custom Build Scripts](https://render.com/docs/deploy-hooks)
- [Plotly Image Export Docs](https://plotly.com/python/static-image-export/)
