# Complete Deployment Guide: SkillSync-AI to Render

This is a **complete step-by-step guide** to deploy your SkillSync-AI application to Render with **ONE SINGLE URL** that you can share with anyone.

## 📋 Prerequisites

Before you start, make sure you have:

1. ✅ **GitHub Account** - Your code needs to be on GitHub
2. ✅ **Render Account** - Sign up at https://render.com (free tier available)
3. ✅ **OpenRouter API Key** - Get one at https://openrouter.ai/keys (free tier available)

---

## 🚀 Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

1. **Open your terminal/command prompt**

2. **Navigate to your project folder:**
   ```bash
   cd E:\Buildathon\final\SkillSync-AI
   ```

3. **Check if it's a git repository:**
   ```bash
   git status
   ```
   
   If you see "not a git repository", initialize it:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ready for deployment"
   ```

4. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it (e.g., `skillsync-ai`)
   - Don't initialize with README
   - Click "Create repository"

5. **Push your code to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/skillsync-ai.git
   git branch -M main
   git push -u origin main
   ```
   (Replace `YOUR_USERNAME` with your GitHub username)

---

### Step 2: Get Your OpenRouter API Key

1. Go to https://openrouter.ai/
2. Sign in or create an account
3. Go to https://openrouter.ai/keys
4. Click "Create Key"
5. **Copy the API key** - you'll need it in Step 4

---

### Step 3: Sign Up / Log In to Render

1. Go to https://render.com
2. Click "Get Started" or "Sign Up"
3. Sign up with your GitHub account (recommended) or email
4. Verify your email if needed

---

### Step 4: Create Your Web Service on Render

1. **In Render Dashboard, click "New +"**
   - Select **"Web Service"**

2. **Connect Your Repository:**
   - If not connected, click "Connect account" and authorize Render
   - Find and select your `skillsync-ai` repository
   - Click "Connect"

3. **Configure Your Service:**

   **Basic Settings:**
   - **Name**: `skillsync-app` (or any name you like)
   - **Region**: `Oregon (US West)` (or closest to you)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave **empty** (unless your repo structure is different)
   - **Runtime**: `Python 3`
   - **Plan**: `Free` (or upgrade later)

   **Build & Deploy:**
   - **Build Command**: 
     ```
     pip install -r backend/requirements.txt && cd frontend && npm install && npm run build
     ```
   
   - **Start Command**: 
     ```
     cd backend && gunicorn --bind 0.0.0.0:$PORT --timeout 900 --workers 2 app:app
     ```

4. **Add Environment Variables:**
   
   Click **"Advanced"** → **"Add Environment Variable"** and add these one by one:

   | Key | Value | Notes |
   |-----|-------|-------|
   | `PYTHON_VERSION` | `3.11.0` | Python version |
   | `NODE_VERSION` | `18.x` or `20.x` | **CRITICAL**: Node.js version (must be 18+ for modern dependencies) |
   | `FLASK_ENV` | `production` | Flask environment |
   | `FLASK_SECRET_KEY` | `your-random-secret-key-here` | Generate a random string (e.g., use https://randomkeygen.com/) |
   | `OPENROUTER_API_KEY` | `your-openrouter-api-key` | The API key from Step 2 |

   **Important Notes:**
   - `NODE_VERSION` is **required** - Render needs it to build your React frontend
   - `FLASK_SECRET_KEY` should be a long random string (at least 32 characters)
   - `OPENROUTER_API_KEY` is your actual API key from OpenRouter

5. **Review and Create:**
   - Double-check all settings
   - Click **"Create Web Service"**

---

### Step 5: Wait for Deployment

1. **Render will start building your app** (this takes 5-10 minutes)
   
2. **Watch the build logs:**
   - You'll see it installing Python packages
   - Then installing Node.js packages
   - Then building your React app
   - Finally starting the server

3. **Common things you'll see:**
   - ✅ "Installing dependencies..."
   - ✅ "Building frontend..."
   - ✅ "Build successful"
   - ✅ "Your service is live at https://skillsync-app.onrender.com"

4. **If build fails:**
   - Check the logs for error messages
   - Common issues:
     - Missing `NODE_VERSION` → Add it as environment variable
     - Build errors → Check that all dependencies are in `package.json` and `requirements.txt`
     - API key issues → Verify `OPENROUTER_API_KEY` is set correctly

---

### Step 6: Test Your Deployment

1. **Visit your URL:**
   - You'll see something like: `https://skillsync-app.onrender.com`
   - This is your **ONE SINGLE URL** to share! 🎉

2. **Test the app:**
   - Try uploading a resume
   - Check if the frontend loads correctly
   - Test API calls (open browser DevTools → Network tab)

3. **Check backend health:**
   - Visit: `https://your-app.onrender.com/api/health`
   - Should return JSON with status

---

## 🎯 You're Done!

**Your app is now live!** Share this single URL with anyone:
```
https://your-app-name.onrender.com
```

---

## 🔧 Troubleshooting

### Build Fails: "npm: command not found" or "SyntaxError: Unexpected token"
**Solution:** 
- **CRITICAL**: Make sure `NODE_VERSION` environment variable is set to `18.x` or `20.x` (NOT `8.x` or older)
- Node.js 8.x is too old and doesn't support modern JavaScript syntax
- Go to Render dashboard → Your service → Environment → Edit `NODE_VERSION` → Set to `18.x` → Save

### Build Fails: "dist directory not found"
**Solution:** 
- Check build logs - the frontend build might have failed
- Make sure `npm run build` completes successfully
- Verify all dependencies are in `package.json`

### White Screen / App Doesn't Load
**Solution:**
- Check Render logs for errors
- Verify the build completed successfully
- Make sure `frontend/dist` directory exists after build
- Check browser console for JavaScript errors

### API Calls Fail
**Solution:**
- Verify `OPENROUTER_API_KEY` is set correctly
- Check backend logs in Render dashboard
- Make sure backend is running (check `/api/health` endpoint)

### Slow First Load
**Solution:**
- Free tier services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (this is normal)
- Consider upgrading to a paid plan for production use

### "Service Unavailable" Error
**Solution:**
- Service might be spinning up (wait 30-60 seconds)
- Check if service is running in Render dashboard
- Free tier has limitations - service might be sleeping

---

## 📝 Environment Variables Reference

Here's a quick reference of all environment variables:

| Variable | Required | Example Value | Purpose |
|----------|----------|---------------|---------|
| `PYTHON_VERSION` | ✅ Yes | `3.11.0` | Python runtime version |
| `NODE_VERSION` | ✅ Yes | `18.x` | Node.js version for building frontend |
| `FLASK_ENV` | ✅ Yes | `production` | Flask environment mode |
| `FLASK_SECRET_KEY` | ✅ Yes | Random string | Flask session secret |
| `OPENROUTER_API_KEY` | ✅ Yes | `sk-or-v1-...` | OpenRouter API key |

---

## 🔄 Updating Your App

After making changes to your code:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```

2. **Render will automatically redeploy** (if auto-deploy is enabled)
   - Or manually trigger deployment in Render dashboard

---

## 💡 Tips

1. **Free Tier Limitations:**
   - Services spin down after 15 min of inactivity
   - First request after spin-down is slow (30-60 sec)
   - Consider paid plan for production

2. **Custom Domain:**
   - Paid feature
   - Go to Settings → Custom Domain

3. **Monitoring:**
   - Check logs regularly in Render dashboard
   - Set up alerts for errors (paid feature)

4. **Performance:**
   - Upgrade to paid plan for better performance
   - Consider using a CDN for static assets

---

## 🆘 Need Help?

1. **Check Render Logs:**
   - Go to your service → "Logs" tab
   - Look for error messages

2. **Check Build Logs:**
   - Go to your service → "Events" tab
   - Look for build errors

3. **Test Locally First:**
   ```bash
   # Build frontend
   cd frontend
   npm install
   npm run build
   
   # Run backend
   cd ../backend
   python app.py
   ```

4. **Common Issues:**
   - Missing environment variables
   - Build command errors
   - Port configuration issues

---

## ✅ Deployment Checklist

Before deploying, make sure:

- [ ] Code is pushed to GitHub
- [ ] All dependencies are in `requirements.txt` and `package.json`
- [ ] `render.yaml` is in repository (optional, for blueprint deployment)
- [ ] You have OpenRouter API key
- [ ] You have Render account
- [ ] Environment variables are ready

After deploying, verify:

- [ ] Build completes successfully
- [ ] Service is running (green status)
- [ ] Frontend loads at root URL
- [ ] API endpoints work (`/api/health`)
- [ ] Can upload resume
- [ ] Can generate roadmap

---

## 🎉 Success!

If everything works, you now have:
- ✅ One single URL to share
- ✅ Frontend and backend on same domain
- ✅ No CORS issues
- ✅ Easy to update (just push to GitHub)

**Share your URL and enjoy!** 🚀

