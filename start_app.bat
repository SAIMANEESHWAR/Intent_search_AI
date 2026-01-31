@echo off
echo ========================================
echo Starting Semantic Video Search App
echo ========================================
echo.

echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "uvicorn app:app --reload"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5500
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:5500
echo.
echo Done! Check the two command windows for server logs.
pause

