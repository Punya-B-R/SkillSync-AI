# Single URL Deployment Guide for Render

This guide will help you deploy SkillSync-AI to Render with **ONE SINGLE URL** - the backend serves the frontend!

## What Changed

- ✅ Backend now serves the frontend static files
- ✅ Frontend uses relative API URLs (no CORS issues!)
- ✅ Single service = One URL to share
- ✅ Simpler deployment

## Prerequisites

1. A GitHub account with your code pushed to a repository
2. A Render account (sign up at https://render.com)
3. An OpenRouter API key (get one at https://openrouter.ai/keys)

## Quick Deployment Steps

### Step 1: Push Your Code to GitHub

Make sure all your changes are pushed to GitHub.

### Step 2: Deploy on Render

1. Go to your Render dashboard: https://dashboard.render.com
2. Click **"New +"** and select **"Web Service"**
3. Connect your GitHub repository if you haven't already
4. Select your repository
5. Configure the service:
   - **Name**: `skillsync-app` (or any name you like)
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)` (or your preferred region)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or set to `SkillSync-AI` if your repo root is different)
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt && cd frontend && npm install && npm run build
     ```
   - **Start Command**: 
     ```
     cd backend && gunicorn --bind 0.0.0.0:$PORT --timeout 900 --workers 2 app:app
     ```
   - **Plan**: `Free` (or upgrade for better performance)

6. **Important**: Add Environment Variables:
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Add these variables:
     - `PYTHON_VERSION` = `3.11.0`
     - `NODE_VERSION` = `18.x` (or `20.x`)
     - `FLASK_ENV` = `production`
     - `FLASK_SECRET_KEY` = (Generate a random secret key, or let Render generate it)
     - `OPENROUTER_API_KEY` = (Your OpenRouter API key)

7. Click **"Create Web Service"**

8. Wait for deployment to complete (5-10 minutes)

9. **That's it!** You now have ONE URL to share! 🎉

## Using render.yaml (Blueprint)

Alternatively, you can use the `render.yaml` file:

1. Make sure `render.yaml` is in your repository root
2. In Render dashboard, click **"New +"** → **"Blueprint"**
3. Connect your repository
4. Render will detect and use `render.yaml`
5. **Still need to set**: `OPENROUTER_API_KEY` environment variable manually

## How It Works

- The build process:
  1. Installs Python dependencies
  2. Builds the React frontend (creates `frontend/dist`)
  3. Starts the Flask server

- The Flask server:
  - Serves API routes at `/api/*`
  - Serves frontend static files at all other routes
  - Handles React Router (all routes serve `index.html`)

- Frontend automatically uses `/api` (relative URL) in production

## Testing Your Deployment

1. Visit your Render URL (e.g., `https://skillsync-app.onrender.com`)
2. You should see your React app!
3. Try uploading a resume
4. Check that API calls work (open browser DevTools → Network tab)

## Troubleshooting

### Build Fails

**Error: "npm: command not found"**
- Make sure `NODE_VERSION` environment variable is set (e.g., `18.x`)

**Error: "dist directory not found"**
- Check build logs - the frontend build might have failed
- Make sure `npm run build` completes successfully

**Error: "Module not found"**
- Check that all dependencies are in `package.json` and `requirements.txt`
- Try building locally first: `cd frontend && npm install && npm run build`

### App Doesn't Load

**White screen or 404**
- Check Render logs for errors
- Verify the build completed successfully
- Make sure `frontend/dist` directory exists after build

**API calls fail**
- Check browser console for errors
- Verify `OPENROUTER_API_KEY` is set correctly
- Check backend logs in Render dashboard

### Performance Issues

**Slow first load**
- Free tier services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Consider upgrading to a paid plan for production

## Environment Variables Summary

- `PYTHON_VERSION`: `3.11.0`
- `NODE_VERSION`: `18.x` or `20.x`
- `FLASK_ENV`: `production`
- `FLASK_SECRET_KEY`: (Random secret key)
- `OPENROUTER_API_KEY`: (Your OpenRouter API key)

**Note**: No CORS configuration needed! Frontend and backend are on the same domain.

## Next Steps

- ✅ Share your single URL with anyone!
- Set up a custom domain (paid feature)
- Configure automatic deployments from GitHub
- Upgrade to a paid plan for better performance

## Need Help?

Check the Render logs:
1. Go to your service in Render dashboard
2. Click on **"Logs"** tab
3. Look for errors during build or runtime

