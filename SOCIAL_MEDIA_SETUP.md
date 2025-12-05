# Social Media Preview Setup

## The Problem
WhatsApp (and other platforms) can't access preview images because Streamlit doesn't serve `/assets` as static files.

## The Solution
Use GitHub raw URLs for the preview image:

```
https://raw.githubusercontent.com/Nialljb/FinSim/design/assets/preview.png
```

## Why This Works
- ✅ GitHub serves raw files publicly with proper CORS
- ✅ Works with all social media scrapers (WhatsApp, Twitter, Facebook)
- ✅ No CDN costs
- ✅ Updates automatically when you push changes

## Favicon vs Preview Image

| Asset | How It Works | Status |
|-------|--------------|--------|
| Favicon (`assets/favicon.png`) | Served by Streamlit locally | ✅ Works |
| Preview Image (`assets/preview.png`) | Needs public URL (GitHub raw) | ✅ Fixed |

## Testing

1. **Favicon**: Just check your browser tab - should show icon
2. **WhatsApp**: Share your deployed link - should show preview image
3. **Facebook**: [Sharing Debugger](https://developers.facebook.com/tools/debug/)
4. **Twitter**: [Card Validator](https://cards-dev.twitter.com/validator)

## WhatsApp Cache Issue
WhatsApp caches previews aggressively. If preview doesn't appear:
- Add `?v=2` to your URL to bypass cache
- Or wait 7 days for cache to expire

## Image Specifications
- **Preview**: 1200x630px (or 2.3MB current size is fine)
- **Favicon**: 512x512px (or 1.3MB current size is fine)
