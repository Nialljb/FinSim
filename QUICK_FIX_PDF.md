# Quick Fix: PDF Export on Render

## What Was Changed

### 1. **render-build.sh** (NEW FILE)
- Installs all required system dependencies for Kaleido
- Installs Python packages
- Executable script that Render runs during deployment

### 2. **requirements.txt** (UPDATED)
- Changed `kaleido>=0.2.1` to `kaleido==0.2.1.post1`
- This version has better compatibility with containerized environments

### 3. **render.yaml** (UPDATED)
- Simplified buildCommand to: `./render-build.sh`
- Now uses the dedicated build script instead of inline commands

## How to Deploy

### Option A: Automatic Deployment (If GitHub Auto-Deploy Enabled)
1. Commit these changes:
   ```bash
   git add render-build.sh requirements.txt render.yaml FIX_PDF_EXPORT_RENDER.md QUICK_FIX_PDF.md
   git commit -m "Fix PDF export on Render with Kaleido system dependencies"
   git push origin design
   ```

2. Render will automatically:
   - Detect the changes
   - Run `render-build.sh`
   - Install system dependencies
   - Install Python packages
   - Start the app

### Option B: Manual Deployment
1. Push changes to GitHub (same as above)
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Find your `finsim-app` service
4. Click "Manual Deploy" → "Deploy latest commit"

## Verification After Deployment

1. **Check Build Logs**
   - Go to Render Dashboard → finsim-app → Logs
   - Look for: "✅ System dependencies installed successfully"
   - Look for: "✅ Python packages installed successfully"

2. **Test PDF Export**
   - Navigate to your deployed app
   - Log in
   - Run a simulation
   - Click "📄 Export to PDF"
   - Button should be **enabled** (not grayed out)
   - PDF should download successfully

3. **Check Error Messages**
   - If still shows "⚠️ PDF unavailable", check logs for:
     - Kaleido import errors
     - Missing system library errors
     - Permission errors on render-build.sh

## Troubleshooting

### If PDF still unavailable:

1. **Check Build Script Permissions**
   ```bash
   # Ensure render-build.sh is executable
   chmod +x render-build.sh
   git add render-build.sh
   git commit -m "Make render-build.sh executable"
   git push
   ```

2. **Check Render Logs for Errors**
   - Look for "apt-get" errors
   - Look for "kaleido" import errors
   - Look for "plotly.io" errors

3. **Try Render Shell** (if available on your plan)
   - Go to Render Dashboard → finsim-app → Shell
   - Test Kaleido directly:
     ```python
     import plotly.graph_objects as go
     import plotly.io as pio
     fig = go.Figure()
     img_bytes = pio.to_image(fig, format='png')
     print(f"Success! Generated {len(img_bytes)} bytes")
     ```

4. **Fallback: Disable PDF on Production**
   - If nothing works, the app gracefully falls back to Excel-only
   - Users will see: "⚠️ PDF unavailable - use Excel export"
   - Excel export contains all the same data

## Expected Timeline

- **Build time**: 3-5 minutes (installing system deps)
- **Deploy time**: 1-2 minutes (starting Streamlit)
- **Total**: ~5-7 minutes from push to live

## Success Indicators

✅ Build logs show "System dependencies installed successfully"
✅ Build logs show "Python packages installed successfully"  
✅ App starts without errors
✅ PDF export button is enabled (not grayed out)
✅ PDF downloads successfully
✅ PDF contains charts and data

## If All Else Fails

The app will continue to work with Excel export, which contains:
- All simulation data
- All percentiles and statistics
- All event details
- Comprehensive wealth breakdown

Excel export is actually **more flexible** than PDF because users can:
- Filter and sort data
- Create custom charts
- Analyze specific scenarios
- Import into other tools

## Support

If issues persist after following this guide:
1. Check the full troubleshooting guide in `FIX_PDF_EXPORT_RENDER.md`
2. Review Kaleido GitHub issues: https://github.com/plotly/Kaleido/issues
3. Check Render's Python environment docs: https://render.com/docs/python-version
