# Fixing Blank Page Issue

If your deployed app shows a blank page, follow these steps:

## Step 1: Check Browser Console

1. Open your deployed URL in a browser
2. Press `F12` (or right-click → Inspect)
3. Go to the **Console** tab
4. Look for **red error messages**
5. Share any errors you see

## Step 2: Check Render Logs

1. Go to Render Dashboard → Your Service
2. Click **"Logs"** tab
3. Look for errors related to:
   - Frontend dist directory
   - Missing files
   - Path issues

## Step 3: Check Debug Endpoint

Visit this URL (replace with your app URL):
```
https://your-app.onrender.com/api/debug/frontend
```

This will show:
- If the dist folder exists
- What files are in the dist folder
- The path being used

## Step 4: Common Issues & Fixes

### Issue 1: "Frontend dist directory not found"

**Problem:** The frontend didn't build successfully

**Fix:**
1. Check Render build logs
2. Make sure `npm run build` completed successfully
3. Verify `NODE_VERSION` is set to `18.x` or `20.x`

### Issue 2: JavaScript Errors in Console

**Common errors:**
- `firebase is not defined` → Firebase config missing
- `Cannot read property of undefined` → Missing environment variables
- `Failed to fetch` → API connection issue

**Fix:**
- Check browser console for specific error
- Add missing environment variables in Render
- Check that API endpoints are working

### Issue 3: White Screen / Blank Page

**Possible causes:**
1. **React app not rendering** - Check console for React errors
2. **Missing environment variables** - Firebase config might be missing
3. **API calls failing** - Check Network tab in browser DevTools

**Fix:**
1. Open browser DevTools (F12)
2. Check **Console** tab for errors
3. Check **Network** tab - are files loading? (200 status)
4. Look for failed requests (red)

### Issue 4: Files Not Loading (404 errors)

**Problem:** Static files (JS, CSS) not being served

**Fix:**
1. Check that `frontend/dist` folder exists after build
2. Verify Flask is serving static files correctly
3. Check Render logs for path issues

## Step 5: Quick Diagnostic Commands

After deploying the updated code, check:

1. **Visit root URL:** `https://your-app.onrender.com/`
   - Should show React app

2. **Check API health:** `https://your-app.onrender.com/api/health`
   - Should return JSON

3. **Check debug endpoint:** `https://your-app.onrender.com/api/debug/frontend`
   - Should show dist folder info

## Step 6: If Still Blank

1. **Check if it's a Firebase issue:**
   - If you're using Firebase, add environment variables:
     - `VITE_FIREBASE_API_KEY`
     - `VITE_FIREBASE_AUTH_DOMAIN`
     - `VITE_FIREBASE_PROJECT_ID`
     - etc.
   - Or comment out Firebase code temporarily to test

2. **Check browser compatibility:**
   - Try a different browser
   - Check if JavaScript is enabled

3. **Check Render service status:**
   - Make sure service is "Live" (green)
   - Not "Sleeping" or "Error"

## What I Just Fixed

I've added:
1. ✅ Better error handling in Flask
2. ✅ Debug endpoint at `/api/debug/frontend`
3. ✅ Logging to help identify issues
4. ✅ Vite base path configuration

## Next Steps

1. **Commit and push the changes:**
   ```bash
   git add backend/app.py frontend/vite.config.js
   git commit -m "Add debugging and fix frontend serving"
   git push
   ```

2. **Wait for redeploy**

3. **Check the debug endpoint:**
   - Visit: `https://your-app.onrender.com/api/debug/frontend`
   - This will tell you if the dist folder exists

4. **Check browser console:**
   - Open your app URL
   - Press F12 → Console tab
   - Share any errors you see

## Most Likely Causes

Based on common issues:

1. **Firebase config missing** (if using Firebase)
   - Add Firebase environment variables
   - Or the app might error on Firebase initialization

2. **JavaScript error preventing render**
   - Check browser console
   - Look for import errors or undefined variables

3. **Dist folder path issue**
   - Check `/api/debug/frontend` endpoint
   - Verify the path is correct

Share what you find in:
- Browser console errors
- `/api/debug/frontend` response
- Render logs

And I'll help you fix it!

