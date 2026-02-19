@echo off
echo ==========================================
echo       AssetManager Setup Script
echo ==========================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)
echo [OK] Python found.

:: 2. Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b 1
)
echo [OK] Node.js found.

:: 3. Create Virtual Environment
if not exist venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
) else (
    echo [INFO] Virtual environment already exists.
)

:: 4. Install Backend Dependencies
echo [INFO] Installing backend dependencies...
call venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b 1
)

:: 5. Install Frontend Dependencies
echo [INFO] Installing frontend dependencies...
cd frontend
if not exist node_modules (
    call npm install
) else (
    echo [INFO] node_modules already exists. Skipping npm install.
)
cd ..

echo.
echo ==========================================
echo       Setup Completed Successfully!
echo ==========================================
echo.
echo You can now start the application using 'start_local.bat'.
pause
