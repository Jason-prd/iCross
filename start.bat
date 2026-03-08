@echo off
REM iCross development server launcher
REM Frontend: port 3000 (Vite)
REM Backend: port 8000 (FastAPI)
REM Author: opencode

echo ============================================================
echo iCross Development Server Launcher
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo Backend API Docs: http://localhost:8000/api/v1/docs
echo ============================================================

REM Check required directories and files
if not exist backend\requirements.txt (
    echo ERROR: backend\requirements.txt not found
    pause
    exit /b 1
)
if not exist frontend\package.json (
    echo ERROR: frontend\package.json not found
    pause
    exit /b 1
)

REM Try to detect python command
echo Checking Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo Found: python
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
        echo Found: py
    ) else (
        echo ERROR: Python not found. Please install Python 3.10+ and add to PATH.
        pause
        exit /b 1
    )
)

REM Try to detect npm command
echo Checking npm...
where npm >nul 2>&1
if %errorlevel% equ 0 (
    set NPM_CMD=npm
    echo Found: npm
) else (
    where npm.cmd >nul 2>&1
    if %errorlevel% equ 0 (
        set NPM_CMD=npm.cmd
        echo Found: npm.cmd
    ) else (
        echo ERROR: npm not found. Please install Node.js 18+ and add to PATH.
        pause
        exit /b 1
    )
)

echo.
echo Starting servers...

REM Start backend server in new window
echo Starting backend server...
start "iCross Backend" cmd /k "cd backend && %PYTHON_CMD% -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in new window
echo Starting frontend server...
start "iCross Frontend" cmd /k "cd frontend && %NPM_CMD% run dev"

echo.
echo ============================================================
echo Both servers are starting:
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo Backend API Docs: http://localhost:8000/api/v1/docs
echo.
echo NOTE: Each server runs in its own command window.
echo Press Ctrl+C to stop a server.
echo.
echo Press any key to close this launcher window...
echo ============================================================
pause >nul