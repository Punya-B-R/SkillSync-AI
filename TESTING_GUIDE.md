# Testing Guide - AI Career Roadmap Generator

## Prerequisites Check

### Backend
1. ✅ Flask server running on `http://localhost:5000`
2. ✅ `.env` file with `OPENROUTER_API_KEY` set
3. ✅ All Python dependencies installed

### Frontend
1. ✅ Node.js installed
2. ✅ Dependencies installed (`npm install`)
3. ✅ Vite dev server can start

## Step-by-Step Testing

### 1. Start Backend Server

```bash
cd backend
python app.py
```

**Expected Output:**
```
============================================================
Starting Career Roadmap Generator API
============================================================
✓ OpenRouter API: Connected
✓ Model: meta-llama/llama-3.3-70b-instruct:free
============================================================
Server starting on http://localhost:5000
```

### 2. Start Frontend Server

**In a NEW terminal:**

```bash
cd frontend
npm install  # If not already done
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. Test the Application Flow

#### Step 1: Upload Resume
1. Open `http://localhost:5173` in browser
2. You should see "Upload Your Resume" screen
3. **Test drag & drop:**
   - Drag a PDF/DOCX/TXT file onto the upload area
   - File should appear with name and size
4. **Test file selection:**
   - Click "Choose file"
   - Select a resume file
5. **Click "Upload Resume"**
   - Should show "Uploading..." then success
6. **Click "Analyze with AI"**
   - Should show "AI is analyzing your resume..."
   - After 5-15 seconds, should display profile with:
     - Experience level
     - Skills (color-coded chips)
     - Top strengths
     - Domains
7. **Click "Continue to Domain Selection"**

#### Step 2: Select Tools
1. Should see AI-recommended domains
2. **Click on a domain card** to expand
3. **Select 2-8 tools** by clicking checkboxes
4. **Check selection summary:**
   - Should show "X / 8 tools selected"
   - Should show estimated learning time
5. **Click "Generate My Roadmap"**

#### Step 3: Set Preferences
1. **Adjust hours per week slider** (2-20 hours)
   - Should see intensity indicator change
2. **Select learning style:**
   - Fast Track / Balanced / Flexible
3. **Optional: Set deadline**
   - Check "I have a specific deadline"
   - Select a date
4. **Review summary:**
   - Total tools
   - Estimated weeks
   - Completion date
5. **Click "Generate My Roadmap"**
   - Should show loading screen with progress messages
   - Takes 10-20 seconds

#### Step 4: View Roadmap
1. Should see comprehensive roadmap with:
   - Overview card (duration, completion date)
   - Learning phases (expandable)
   - Weekly schedule (tabs for weeks)
   - Resources library (with filters)
   - Project ideas (expandable)
   - Career insights
   - Skill gap analysis
2. **Test AI Chat:**
   - Click chat bubble (bottom-right)
   - Ask a question
   - Should get AI response
3. **Test export:**
   - Click "Export PDF" (opens print dialog)
   - Click "Copy" (copies markdown to clipboard)

## Quick Test Checklist

- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors
- [ ] Can upload a resume file
- [ ] AI analysis works and shows profile
- [ ] Domain recommendations load
- [ ] Can select tools (2-8)
- [ ] Preferences can be set
- [ ] Roadmap generates successfully
- [ ] Roadmap displays all sections
- [ ] AI Chat works
- [ ] Navigation (back/start over) works
- [ ] Error messages display properly

## Common Issues & Solutions

### Backend Issues

**Problem:** "OPENROUTER_API_KEY not found"
- **Solution:** Create `.env` file in `backend/` with your API key

**Problem:** "Module not found"
- **Solution:** Run `pip install -r requirements.txt` in backend folder

**Problem:** Port 5000 already in use
- **Solution:** Change port in `app.py` or kill process using port 5000

### Frontend Issues

**Problem:** "Cannot connect to API"
- **Solution:** Make sure backend is running on `http://localhost:5000`
- **Check:** `frontend/src/services/api.js` has correct `API_BASE_URL`

**Problem:** "Module not found" in frontend
- **Solution:** Run `npm install` in frontend folder

**Problem:** CORS errors
- **Solution:** Backend CORS is configured for `localhost:5173` and `localhost:3000`

### AI/API Issues

**Problem:** "Analysis failed" or timeout
- **Solution:** Check OpenRouter API key is valid
- **Solution:** Check internet connection
- **Solution:** Free tier may have rate limits

## Manual API Testing

You can also test API endpoints directly:

### Test Health Check
```bash
curl http://localhost:5000/api/health
```

### Test Analyze Resume
```bash
curl -X POST http://localhost:5000/api/analyze-resume \
  -H "Content-Type: application/json" \
  -d "{\"resume_text\": \"John Doe\nSoftware Engineer\n5 years experience\nSkills: Python, React\"}"
```

## Expected Behavior

- **Upload:** Should accept PDF, DOCX, TXT files up to 5MB
- **Analysis:** Takes 5-15 seconds, returns structured profile
- **Recommendations:** Returns 6-8 domain recommendations
- **Roadmap Generation:** Takes 10-20 seconds, returns comprehensive roadmap
- **Chat:** Real-time responses, maintains conversation history

## Performance Expectations

- File upload: < 2 seconds
- Resume analysis: 5-15 seconds
- Domain recommendations: 5-10 seconds
- Roadmap generation: 10-20 seconds
- Chat responses: 3-8 seconds


