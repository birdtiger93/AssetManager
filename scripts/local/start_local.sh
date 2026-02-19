#!/bin/bash

# Ensure script is run from project root
cd "$(dirname "$0")/../.."

echo "Starting KIS Asset Manager..."

# 1. Start Backend in background
echo "Launching Backend (FastAPI)..."
python3 -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# 2. Start Frontend in background
echo "Launching Frontend (Vite)..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "All systems launching!"
echo "Dashboard: http://localhost:5173"
echo "API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

# Trap SIGINT (Ctrl+C) to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID" SIGINT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
