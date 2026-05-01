@echo off
title NeuroPilot AI Elite - Orchestrator
echo [System] Initializing Elite DevOps Orchestrator...

if "%OPENAI_API_KEY%"=="" (
    echo [Warning] OPENAI_API_KEY is not set!
    echo Please set it using: set OPENAI_API_KEY=sk-xxxx
    echo or add it to your system environment variables.
    pause
)

python main.py
pause
