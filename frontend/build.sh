#!/bin/bash
# Build script for Render deployment
# This script builds the frontend with the correct API URL

set -e  # Exit on any error

echo "Starting build process..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Check if installation was successful
if [ $? -ne 0 ]; then
  echo "Error: npm install failed"
  exit 1
fi

# Get API URL from environment variable
# If VITE_API_URL is not set, we'll need to set it manually after backend deploys
API_URL=${VITE_API_URL}

if [ -z "$API_URL" ]; then
  echo "Warning: VITE_API_URL not set. Using placeholder."
  echo "You'll need to update the build command with your backend URL after deployment."
  API_URL="https://skillsync-backend.onrender.com"
fi

echo "Building frontend with API URL: $API_URL"

# Build with the API URL
VITE_API_URL=$API_URL npm run build

# Check if build was successful
if [ $? -ne 0 ]; then
  echo "Error: Build failed"
  exit 1
fi

# Verify dist directory exists
if [ ! -d "dist" ]; then
  echo "Error: dist directory was not created"
  exit 1
fi

echo "Build complete! dist directory created successfully."
ls -la dist/

