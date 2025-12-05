# Social Media Preview Setup for FinSTK

## What Was Added

### 1. Favicon
- **File**: `assets/favicon.png`
- **Usage**: Browser tab icon
- **Implementation**: Added to `st.set_page_config()` via `page_icon="assets/favicon.png"`

### 2. Preview Image
- **File**: `assets/preview.png`
- **Usage**: Social media link previews (Facebook, Twitter, LinkedIn, Slack, etc.)
- **Implementation**: Added via Open Graph and Twitter Card meta tags

### 3. Meta Tags
Added comprehensive social media meta tags:
- **Open Graph** (Facebook, LinkedIn, Discord)
- **Twitter Cards** (Twitter/X)
- **Standard SEO** (Google, search engines)

## Files Modified

### `wealth_simulator.py`
**Updated Page Config:**
```python
st.set_page_config(
    page_title="FinSTK - Financial Simulation Toolkit",
    page_icon="assets/favicon.png",  # ← Favicon added
    layout="wide",
    menu_items={...},
    initial_sidebar_state="expanded"
)
```

**Added Social Meta Tags:**
```html
<meta property="og:title" content="FinSTK - Financial Simulation Toolkit" />
<meta property="og:description" content="..." />
<meta property="og:image" content="https://finstk.com/assets/preview.png" />
<meta property="og:url" content="https://finstk.com" />
<meta property="og:type" content="website" />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="FinSTK - Financial Simulation Toolkit" />
<meta name="twitter:description" content="..." />
<meta name="twitter:image" content="https://finstk.com/assets/preview.png" />
```

## Deployment Steps

### Step 1: Ensure Assets are Accessible on Render

The meta tags reference `https://finstk.com/assets/preview.png`. You need to:

**Option A: Serve Static Files via Streamlit (Recommended)**
1. Keep assets in `/assets` directory
2. No additional configuration needed
3. Streamlit automatically serves files from the app directory

**Option B: Use Custom Domain or CDN**
1. Upload `preview.png` to a CDN or static hosting
2. Update the meta tag URLs to point to the CDN location

### Step 2: Update URLs in Meta Tags (If Needed)

If your domain is different from `finstk.com`, update these lines in `wealth_simulator.py`:

```python
# Change these URLs to match your actual domain
<meta property="og:image" content="https://YOUR-DOMAIN.com/assets/preview.png" />
<meta property="og:url" content="https://YOUR-DOMAIN.com" />
<meta name="twitter:image" content="https://YOUR-DOMAIN.com/assets/preview.png" />
```

### Step 3: Deploy to Render

```bash
git add assets/ wealth_simulator.py SOCIAL_MEDIA_SETUP.md
git commit -m "Add favicon and social media preview images"
git push origin design
```

Render will automatically deploy if auto-deploy is enabled.

### Step 4: Test Social Media Previews

After deployment, test your link previews:

#### Facebook/LinkedIn Debugger
1. Go to [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
2. Enter your URL: `https://your-render-app.onrender.com`
3. Click "Debug"
4. Should show:
   - ✅ Title: "FinSTK - Financial Simulation Toolkit"
   - ✅ Description: "Plan your financial future with Monte Carlo simulations..."
   - ✅ Image: Your preview.png

#### Twitter Card Validator
1. Go to [Twitter Card Validator](https://cards-dev.twitter.com/validator)
2. Enter your URL
3. Click "Preview Card"
4. Should show large image card with title, description, and preview

#### Other Platforms
- **Slack**: Paste link in a channel - should show rich preview
- **Discord**: Paste link in a server - should show embed with image
- **LinkedIn**: Share link - should show card with preview image
- **WhatsApp**: Send link - should show preview (mobile)

## Recommended Image Specs

### Favicon (`favicon.png`)
- **Size**: 512x512px or 256x256px
- **Format**: PNG with transparency
- **File size**: < 100KB
- **Content**: Simple, recognizable icon (e.g., dolphin emoji 🐬 or FinSTK logo)

### Preview Image (`preview.png`)
- **Size**: 1200x630px (Facebook/LinkedIn optimal)
- **Aspect ratio**: 1.91:1
- **Format**: PNG or JPG
- **File size**: < 1MB (preferably < 500KB)
- **Content**: 
  - FinSTK branding
  - Key value proposition text
  - Visually appealing graphics
  - High contrast for readability
  - No critical text within 40px of edges

## Troubleshooting

### Preview Not Showing

1. **Check Image URL**
   - Verify `https://finstk.com/assets/preview.png` is accessible
   - Open URL directly in browser
   - Should download/display the image

2. **Clear Social Media Cache**
   - Facebook: Use sharing debugger and click "Scrape Again"
   - Twitter: Cards are cached for ~7 days
   - LinkedIn: No direct cache clearing, wait 24 hours

3. **Check Image Format**
   - Must be PNG or JPG
   - No WEBP (not supported by all platforms)
   - File must be < 8MB

4. **Verify HTTPS**
   - Social platforms require HTTPS for images
   - HTTP will not work

### Favicon Not Showing

1. **Clear Browser Cache**
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Clear cache and reload

2. **Check File Path**
   - Verify `assets/favicon.png` exists
   - Check file permissions

3. **Wait for Browser Update**
   - Favicons can take time to update
   - Try different browser

### Meta Tags Not Working

1. **Check HTML Rendering**
   - View page source (Ctrl+U)
   - Search for `<meta property="og:image"`
   - Should appear in `<head>` section

2. **Streamlit Limitation**
   - Streamlit may not inject meta tags in time for crawlers
   - Consider using custom `index.html` if needed

## Advanced: Custom Index.html (If Meta Tags Don't Work)

If Streamlit's meta tag injection doesn't work for crawlers, create a custom landing page:

**`.streamlit/config.toml`:**
```toml
[server]
enableStaticServing = true
```

**`static/index.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta property="og:title" content="FinSTK - Financial Simulation Toolkit" />
    <meta property="og:description" content="..." />
    <meta property="og:image" content="https://finstk.com/assets/preview.png" />
    <meta http-equiv="refresh" content="0;url=/app" />
</head>
<body>Redirecting...</body>
</html>
```

## Verification Checklist

After deployment:

- [ ] Favicon appears in browser tab
- [ ] Facebook debugger shows correct preview
- [ ] Twitter card validator shows correct preview
- [ ] Slack link preview works
- [ ] Discord embed shows correctly
- [ ] LinkedIn share shows preview
- [ ] Preview image loads at full URL
- [ ] Title and description are correct
- [ ] Image is high quality and properly sized

## Support

If previews still don't work after following this guide:
1. Check Render deployment logs for errors
2. Verify asset files uploaded correctly
3. Test image URLs directly in browser
4. Use social media debugging tools
5. Wait 24-48 hours for cache updates
