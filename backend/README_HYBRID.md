# MyHaven Hybrid: MuRIL-BERT + Groq Architecture

This directory contains the **Hybrid (MuRIL-BERT + Groq)** version of MyHaven.

## How it works

1. **User sends message** (English, Hindi, or Hinglish).
2. **MuRIL-BERT executes FIRST**:
   - Classifies emotion into 8 classes: `joy`, `sadness`, `fear`, `anger`, `surprise`, `neutral`, `disgust`, `shame`.
   - Computes confidence and emotion intensity.
3. **Dynamic Prompt Conditioning**:
   - The detected emotion & specific empathy guidance are injected directly into the LLM system prompt before response generation.
4. **Groq LLM Generates Empathetic Response**:
   - Groq (`llama-3.3-70b-versatile` or configured fallback) creates the empathetic, personalized response attuned directly to the user's emotional state.
5. **Auto Diary & Memory Logging**:
   - The emotion and chat are saved to SQLite (`myhaven.db`).

---

## How to Fine-Tune the MuRIL Emotion Head

1. **Compile Dataset**:
   ```powershell
   ..\.venv\Scripts\python.exe build_finetune_dataset.py
   ```
2. **Train MuRIL Classifier**:
   ```powershell
   ..\.venv\Scripts\python.exe train_muril_emotion.py
   ```
   This will train on the multilingual dataset and output `muril_emotion_model.pth`.

---

## How to Run Locally

```powershell
..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```
(Runs on port 8001 so it doesn't collide with the cloud-light version on port 8000).

---

## Hosting Notes

- **Local / VPS / Hugging Face Spaces (>= 2GB RAM)**: Keep `USE_LOCAL_ML=true` in `.env` to use the full MuRIL PyTorch weights.
- **Low RAM Cloud Hosts (Render 512MB free tier)**: Set `USE_LOCAL_ML=false` or use the root `backend/` folder.
