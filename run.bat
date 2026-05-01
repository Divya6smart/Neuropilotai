@echo off
title NeuroPilot AI Elite - Orchestrator
echo [System] Clearing port 8000...
powershell -Command "$p = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue; if ($p) { Stop-Process -Id $p.OwningProcess -Force }"
echo [System] Initializing Elite DevOps Orchestrator...

if "%OPENAI_API_KEY%"=="" (
    if not exist .env (
        echo [Warning] OPENAI_API_KEY is not set and .env file is missing!
        echo Please create a .env file with: OPENAI_API_KEY=sk-xxxx
        echo or set it using: set OPENAI_API_KEY=sk-xxxx
        pause
    )
)

python main.py
pause
