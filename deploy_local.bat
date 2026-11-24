@echo off
title Cricket Kit Management System - Production Server
echo =========================================================
echo   🏏 Cricket Kit Management System - Production WSGI
echo =========================================================
echo.
echo Launching your browser at http://localhost:5000 ...
start http://localhost:5000
echo.
echo Starting Waitress Production WSGI Server on port 5000...
echo (Press Ctrl+C to stop)
python wsgi.py
pause
