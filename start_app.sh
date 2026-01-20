#!/bin/bash
echo "🚀 Starting CineMatrix..."

# Kill existing processes
echo "Killing existing processes on ports 3000, 4000, 7000, 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:7000 | xargs kill -9 2>/dev/null
lsof -ti:4000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start Backend in background
echo "Starting Backend API (Port 7000)..."
source venv/bin/activate
nohup python backend/api/server.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID)"

# Start Frontend
echo "Starting Frontend (Port 4000)..."
cd frontend
npm run dev -- -p 4000

# Cleanup on exit
kill $BACKEND_PID
