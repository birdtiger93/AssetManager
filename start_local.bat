@echo off
echo Starting KIS Asset Manager...

:: 1. Start Backend in a new window
echo Launching Backend (FastAPI)...
start "KIS Backend" cmd /k "python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8000 --reload"

:: 2. Start Frontend in a new window
echo Launching Frontend (Vite)...
cd frontend
start "KIS Frontend" cmd /k "npm run dev"

echo.
echo All systems launching!
echo Dashboard: http://localhost:5173
echo API Docs: http://127.0.0.1:8000/docs
echo.
pause
