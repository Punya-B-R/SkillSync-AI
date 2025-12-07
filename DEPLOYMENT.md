# Deployment Guide for Render

This guide will help you deploy SkillSync-AI to Render.

## Prerequisites

1. A GitHub account with your code pushed to a repository
2. A Render account (sign up at https://render.com)
3. An OpenRouter API key (get one at https://openrouter.ai/keys)

## Deployment Steps

### Step 1: Push Your Code to GitHub

Make sure your code is pushed to a GitHub repository. Render will automatically deploy from your GitHub repository.

### Step 2: Deploy Backend Service

1. Go to your Render dashboard: https://dashboard.render.com
2. Click **"New +"** and select **"Web Service"**
3. Connect your GitHub repository if you haven't already
4. Select your repository
5. Configure the backend service:
   - **Name**: `skillsync-backend`
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or set to `SkillSync-AI` if your repo root is different)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn --bind 0.0.0.0:$PORT --timeout 900 --workers 2 app:app`
   - **Plan**: `Free`

6. Add Environment Variables:
   - `PYTHON_VERSION` = `3.11.0`
   - `FLASK_ENV` = `production`
   - `FLASK_SECRET_KEY` = (Generate a random secret key)
   - `OPENROUTER_API_KEY` = (Your OpenRouter API key)
   - `ALLOWED_ORIGINS` = (Leave empty for now, we'll set this after frontend deploys)

7. Click **"Create Web Service"**

8. Wait for the backend to deploy. Note the URL (e.g., `https://skillsync-backend.onrender.com`)

### Step 3: Deploy Frontend Service

1. In your Render dashboard, click **"New +"** and select **"Static Site"**
2. Select your repository
3. Configure the frontend service:
   - **Name**: `skillsync-frontend`
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or set to `SkillSync-AI` if your repo root is different)
   - **Build Command**: `cd frontend && npm install && VITE_API_URL=https://YOUR-BACKEND-URL.onrender.com npm run build`
     - Replace `YOUR-BACKEND-URL` with your actual backend URL from Step 2 (e.g., `skillsync-backend.onrender.com`)
     - Make sure to include `https://` in the URL
   - **Publish Directory**: `frontend/dist`
   - **Plan**: `Free`

4. Click **"Create Static Site"**

5. Wait for the frontend to deploy. Note the URL (e.g., `https://skillsync-frontend.onrender.com`)

### Step 4: Update Backend CORS Settings

1. Go back to your backend service in Render
2. Go to **Environment** tab
3. Update the `ALLOWED_ORIGINS` environment variable:
   - Set it to your frontend URL: `https://skillsync-frontend.onrender.com`
   - Or if you want to allow multiple origins: `https://skillsync-frontend.onrender.com,https://your-custom-domain.com`

4. Click **"Save Changes"** - this will trigger a redeploy

### Step 5: Update Frontend Build Command (if needed)

If you need to update the API URL later:

1. Go to your frontend service in Render
2. Go to **Settings** tab
3. Update the **Build Command** to use the correct backend URL:
   ```
   cd frontend && npm install && VITE_API_URL=https://skillsync-backend.onrender.com npm run build
   ```
4. Click **"Save Changes"** - this will trigger a redeploy

## Alternative: Using render.yaml (Blueprints)

If you prefer to use the `render.yaml` file:

1. Make sure your `render.yaml` is in the root of your repository
2. In Render dashboard, click **"New +"** and select **"Blueprint"**
3. Connect your repository and select it
4. Render will automatically detect and use your `render.yaml` file
5. You'll still need to manually set the `OPENROUTER_API_KEY` environment variable in the backend service
6. After both services deploy, update the `ALLOWED_ORIGINS` in the backend service

**Note**: When using render.yaml, you may need to manually update the frontend build command with the actual backend URL after deployment.

## Environment Variables Summary

### Backend Service
- `PYTHON_VERSION`: `3.11.0`
- `FLASK_ENV`: `production`
- `FLASK_SECRET_KEY`: (Random secret key)
- `OPENROUTER_API_KEY`: (Your OpenRouter API key)
- `ALLOWED_ORIGINS`: (Your frontend URL, e.g., `https://skillsync-frontend.onrender.com`)

### Frontend Service
- The API URL is set during build time via the build command

## Troubleshooting

### Backend Issues

1. **Build fails**: Check that all dependencies are in `backend/requirements.txt`
2. **Service crashes**: Check the logs in Render dashboard
3. **CORS errors**: Make sure `ALLOWED_ORIGINS` is set correctly with your frontend URL

### Frontend Issues

1. **Build fails**: Check that all dependencies are in `frontend/package.json`
2. **"Publish directory frontend/dist does not exist" error**:
   - This means the build command failed before creating the dist directory
   - Check the build logs in Render dashboard for specific errors
   - Make sure your build command is: `cd frontend && npm install && VITE_API_URL=https://YOUR-BACKEND-URL.onrender.com npm run build`
   - Verify that `npm run build` completes successfully (check logs)
   - Ensure you're in the `frontend` directory when running the build
   - Try the build command locally first: `cd frontend && npm install && npm run build`
3. **API calls fail**: Verify the `VITE_API_URL` in the build command matches your backend URL
4. **404 errors**: Make sure the `staticPublishPath` is set to `frontend/dist`

### Common Issues

1. **Services not connecting**: 
   - Verify backend is running (check health endpoint: `https://your-backend.onrender.com/`)
   - Check CORS settings in backend
   - Verify API URL in frontend build command

2. **Timeout errors**: 
   - The backend is configured with a 900-second timeout for long-running AI requests
   - If you need longer, you may need to upgrade to a paid plan

3. **Free tier limitations**:
   - Services on the free tier spin down after 15 minutes of inactivity
   - First request after spin-down may take 30-60 seconds
   - Consider upgrading to a paid plan for production use

## Testing Your Deployment

1. Visit your frontend URL
2. Try uploading a resume
3. Check browser console for any errors
4. Check backend logs in Render dashboard for API calls

## Next Steps

- Set up a custom domain (paid feature)
- Configure automatic deployments from GitHub
- Set up monitoring and alerts
- Consider upgrading to a paid plan for better performance

