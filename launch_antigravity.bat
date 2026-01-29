@echo off
title ANTIGRAVITY - System Check & Launch
echo [1/4] Verification des serveurs...

:: 1. Demarrage MySQL
net start MySQL80 >nul 2>&1

:: 2. Mise a jour
echo [2/4] Verification des mises a jour...
git pull origin main --quiet

:: 3. Demarrage des Backends (Node et Python)
echo [3/4] Lancement des coeurs logiques...
start /min cmd /c "cd backend-node && node index.js"

:: 4. Notification Vocale et Lancement Front
echo [4/4] Finalisation...
powershell -ExecutionPolicy Bypass -File "voice_check.ps1"

cd "frontend-angular"
start /min cmd /c "ng serve --open"

echo.
echo ==========================================
echo    SYSTEME ANTIGRAVITY OPERATIONNEL
echo ==========================================
exit
