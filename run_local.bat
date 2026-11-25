@echo off
echo ============================================================
echo   Starting MyHaven Hybrid (MuRIL-BERT + Groq)
echo ============================================================
echo.
cd /d "%~dp0backend"

if exist "..\..\haven-code-main\.venv\Scripts\python.exe" (
    set "PY_CMD=..\..\haven-code-main\.venv\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

echo Using Python: %PY_CMD%
%PY_CMD% -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
