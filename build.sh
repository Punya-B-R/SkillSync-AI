#!/bin/bash
# Unified build script for Render deployment
# Builds both frontend and backend

set -e  # Exit on any error

echo "Starting unified build process..."

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "Build complete!"

