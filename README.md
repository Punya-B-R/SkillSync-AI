# SkillSync - AI-Powered Career Roadmap Generator
LIVE DEMO LINK: https://skillsync-ai-2-w9jj.onrender.com/

A full-stack application that generates personalized career roadmaps using AI (OpenRouter with Llama 3.3 70B).

## Tech Stack

- **Backend**: Python Flask (REST API)
- **Frontend**: React + Vite + Tailwind CSS
- **AI**: OpenRouter API (meta-llama/llama-3.3-70b-instruct:free)
- **File Processing**: PyPDF2, python-docx

## Project Structure

```
/backend
  /api          - API routes
  /services     - Business logic (resume parsing, AI, roadmap generation)
  /utils        - Utility functions (file handling, prompts)
  app.py        - Flask application entry point
  requirements.txt

/frontend
  /src
    /components - React components
    /services   - API service layer
    /utils      - Helper functions
    App.jsx     - Main application component
    main.jsx    - Entry point
  package.json
  vite.config.js
  tailwind.config.js
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file (copy from `env.example.txt`):
```bash
# Copy env.example.txt to .env and add your OpenRouter API key
OPENROUTER_API_KEY=your_openrouter_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

6. Run the Flask server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## API Endpoints

- `POST /api/upload-resume` - Upload and parse resume file
- `POST /api/analyze-resume` - Analyze resume using AI
- `POST /api/recommend-domains` - Get recommended career domains
- `POST /api/generate-roadmap` - Generate career roadmap
- `POST /api/chat` - AI chat for roadmap questions

## Development Notes

All implementation files contain TODO comments indicating what needs to be implemented. The structure is set up and ready for development.

## Getting an OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign in or create an account
3. Go to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Add it to your `.env` file as `OPENROUTER_API_KEY`

**Note**: The app uses the free tier model `meta-llama/llama-3.3-70b-instruct:free` which doesn't require credits for basic usage.

