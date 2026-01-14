#!/bin/bash
echo "🚀 Starting CineMatrix..."

# Start Backend in background
echo "Starting Backend API (Port 8000)..."
source venv/bin/activate
nohup python backend/api/server.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID)"

# Start Frontend
echo "Starting Frontend (Port 5173)..."
cd frontend
npm run dev

# Cleanup on exit
kill $BACKEND_PID
