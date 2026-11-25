@echo off
echo ============================================================
echo   Fine-Tuning MuRIL Emotion Classifier
echo ============================================================
echo.
cd /d "%~dp0backend"

if exist "..\..\haven-code-main\.venv\Scripts\python.exe" (
    set "PY_CMD=..\..\haven-code-main\.venv\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

echo Step 1: Compiling balanced dataset...
%PY_CMD% build_finetune_dataset.py

echo.
echo Step 2: Training MuRIL PyTorch classification head...
%PY_CMD% train_muril_emotion.py

echo.
echo Fine-tuning complete! Weights saved to backend\muril_emotion_model.pth.
pause
