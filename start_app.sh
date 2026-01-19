#!/bin/bash
echo "🚀 Starting CineMatrix..."

# Kill existing processes
echo "Killing existing processes on ports 8000 (Backend), 3000 (Frontend), and 5173 (Vite)..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

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
