#!/bin/bash

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Install backend dependencies
cd backend
pip install -r requirements.txt
