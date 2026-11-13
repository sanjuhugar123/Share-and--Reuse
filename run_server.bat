@echo off
title Share and Reuse Web Platform
cd /d %~dp0
echo =========================================================
echo    SHARE AND REUSE - Food and Clothes Redistribution
echo =========================================================
echo  Starting web platform...
echo  Local URL: http://127.0.0.1:5000
echo  Press Ctrl+C anytime to stop the server.
echo =========================================================
start http://127.0.0.1:5000
.\venv\Scripts\python.exe app.py
pause
