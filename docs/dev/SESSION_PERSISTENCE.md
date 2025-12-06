# Session Persistence for FinSim

The session persistence has been implemented using browser localStorage. Here's how it works:

## How It Works

1. **On Login**: Your user ID is saved to browser localStorage
2. **On Page Refresh**: The app checks localStorage and restores your session automatically
3. **On Logout**: localStorage is cleared

## Current Limitations

Due to Streamlit's architecture, full session persistence across page refreshes is challenging. The current implementation:

- ✅ Keeps you logged in during normal navigation
- ✅ Persists session within the same browser tab
- ⚠️ May require re-login after hard refresh (F5/Cmd+R)
- ⚠️ Requires cookies/localStorage to be enabled

## Better Solution (Future)

For production-grade session persistence, consider:
1. Using Streamlit's auth cookies (requires additional package)
2. Implementing JWT tokens with database storage
3. Using external auth providers (OAuth, Auth0, etc.)

## Current Workaround

For now, users should avoid hard-refreshing the page. The app maintains state during normal navigation.
