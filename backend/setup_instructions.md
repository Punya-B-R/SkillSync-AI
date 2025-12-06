# Flask Installation Troubleshooting

## Step 1: Check which Python you're using

Run these commands in your terminal (in the `backend` folder):

```bash
# Check Python version
python --version

# Check pip version
pip --version

# Check where Python is located
python -c "import sys; print(sys.executable)"

# Check if Flask is installed
python -c "import flask; print(flask.__version__)"
```

## Step 2: Create and activate virtual environment (RECOMMENDED)

```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

## Step 3: Install dependencies in virtual environment

```bash
# Make sure virtual environment is activated (you should see (venv))
pip install -r requirements.txt

# Verify Flask is installed
pip list | findstr flask
# or on Linux/Mac:
pip list | grep flask
```

## Step 4: Run the app

```bash
# Make sure you're in the backend folder
# Make sure virtual environment is activated
python app.py
```

## Alternative: Install directly (if not using venv)

If you're not using a virtual environment:

```bash
# Try pip3 instead of pip
pip3 install -r requirements.txt

# Or use python -m pip
python -m pip install -r requirements.txt

# Or specify Python version explicitly
py -3 -m pip install -r requirements.txt
```

## If still not working:

1. **Check IDE Python interpreter**: Make sure your IDE (VS Code, PyCharm, etc.) is using the same Python where Flask is installed
2. **Reinstall Flask**: `pip uninstall flask` then `pip install flask==3.0.0`
3. **Check PATH**: Make sure Python is in your system PATH

