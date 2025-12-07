# Deployment Troubleshooting Guide

## Common Build Errors and Solutions

### ❌ Error: "SyntaxError: Unexpected token" or Node.js version issues

**Problem:** Node.js version is too old (8.x or lower)

**Solution:**
1. Go to Render Dashboard → Your Service → Environment
2. Find `NODE_VERSION` environment variable
3. Change it to `18.x` or `20.x`
4. Save and redeploy

---

### ❌ Error: "dist directory not found" or "Publish directory does not exist"

**Problem:** Frontend build failed before creating dist folder

**Possible Causes:**
1. Node.js version too old (see above)
2. Missing dependencies in package.json
3. Build command error

**Solution:**
1. Check build logs for specific npm errors
2. Verify `NODE_VERSION` is set to `18.x` or `20.x`
3. Make sure build command is:
   ```
   pip install -r backend/requirements.txt && cd frontend && npm install && npm run build
   ```

---

### ❌ Error: "Module not found" or "Cannot find module"

**Problem:** Missing dependencies

**Solution:**
1. Check that all dependencies are in `package.json` (frontend) or `requirements.txt` (backend)
2. Try building locally first:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

---

### ❌ Error: "pip: command not found" or Python issues

**Problem:** Python not installed or wrong version

**Solution:**
1. Make sure `PYTHON_VERSION` is set to `3.11.0` in environment variables
2. Verify build command includes: `pip install -r backend/requirements.txt`

---

### ❌ Error: "gunicorn: command not found"

**Problem:** Gunicorn not installed

**Solution:**
1. Check that `gunicorn==21.2.0` is in `backend/requirements.txt`
2. Verify build command installs requirements: `pip install -r backend/requirements.txt`

---

### ❌ Error: "Port already in use" or "Address already in use"

**Problem:** Wrong start command

**Solution:**
Make sure start command is:
```
cd backend && gunicorn --bind 0.0.0.0:$PORT --timeout 900 --workers 2 app:app
```

**Important:** Use `$PORT` (not a fixed port number)

---

### ❌ Error: "OPENROUTER_API_KEY not set" or API errors

**Problem:** Missing environment variable

**Solution:**
1. Go to Environment tab
2. Add `OPENROUTER_API_KEY` with your actual API key
3. Make sure there are no extra spaces

---

### ❌ Error: "Cannot GET /" or white screen

**Problem:** Frontend not being served correctly

**Possible Causes:**
1. Frontend build didn't complete
2. dist folder not in correct location
3. Flask not configured to serve static files

**Solution:**
1. Check that `frontend/dist` exists after build
2. Verify `backend/app.py` has the serve_frontend function
3. Check build logs to ensure `npm run build` completed

---

### ❌ Error: "CORS error" or API calls fail

**Problem:** CORS configuration issue (shouldn't happen with single service)

**Solution:**
- With single service deployment, CORS shouldn't be an issue
- If you see CORS errors, check that frontend is using relative URLs (`/api` not `http://...`)

---

## How to Check Build Logs

1. **In Render Dashboard:**
   - Go to your service
   - Click "Logs" tab
   - Scroll to see build output
   - Look for red error messages

2. **What to look for:**
   - ✅ "Successfully installed..." = Good
   - ✅ "Build successful" = Good
   - ❌ "SyntaxError" = Node.js version issue
   - ❌ "npm ERR!" = npm/dependency issue
   - ❌ "Module not found" = Missing dependency
   - ❌ "Exited with status 1" = Build failed

---

## Step-by-Step Debugging

1. **Check Environment Variables:**
   - `PYTHON_VERSION` = `3.11.0`
   - `NODE_VERSION` = `18.x` or `20.x` (NOT 8.x!)
   - `FLASK_ENV` = `production`
   - `FLASK_SECRET_KEY` = (set)
   - `OPENROUTER_API_KEY` = (set)

2. **Check Build Command:**
   ```
   pip install -r backend/requirements.txt && cd frontend && npm install && npm run build
   ```

3. **Check Start Command:**
   ```
   cd backend && gunicorn --bind 0.0.0.0:$PORT --timeout 900 --workers 2 app:app
   ```

4. **Test Locally First:**
   ```bash
   # Test frontend build
   cd frontend
   npm install
   npm run build
   
   # Test backend
   cd ../backend
   pip install -r requirements.txt
   python app.py
   ```

---

## Quick Fixes Checklist

- [ ] `NODE_VERSION` is `18.x` or `20.x` (NOT 8.x)
- [ ] `PYTHON_VERSION` is `3.11.0`
- [ ] All environment variables are set
- [ ] Build command is correct
- [ ] Start command uses `$PORT`
- [ ] `gunicorn` is in requirements.txt
- [ ] All dependencies are in package.json/requirements.txt

---

## Still Having Issues?

1. **Share the exact error message** from Render logs
2. **Check the "Events" tab** for deployment history
3. **Try manual deploy** (Settings → Manual Deploy)
4. **Verify your code works locally** before deploying

