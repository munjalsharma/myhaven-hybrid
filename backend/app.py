# -*- coding: utf-8 -*-
"""
MyHaven - Hugging Face Spaces Optimized Server
Direct Gradio Blocks Application with full Hugging Face Spaces compatibility.
Zero port conflicts, zero process exit, native Gradio SDK execution.
"""

import os
import gradio as gr
from mindmate_integration import MindMateSentimentAnalyzer
from main import detect_emotion, groq_chat, detect_sentiment, db_add_diary_entry, db_get_user, db_clear_user, db_full_reset_user, db_get_messages

print("=" * 60)
print("STARTING HUGGING FACE SPACES MYHAVEN APP")
print("=" * 60)

# Pre-initialize analyzer
analyzer = MindMateSentimentAnalyzer(model_path="muril_emotion_model.pth")

# Custom API endpoint handlers inside Gradio
def api_chat(user_id, message, persona_hint=""):
    if not message or not message.strip():
        return {"error": "Empty message"}
        
    el, ec, ee, en = detect_emotion(message)
    emotion_payload = {"label": el, "confidence": ec, "emoji": ee}
    reply = groq_chat(user_id, message, persona_hint=persona_hint, emotion_info=emotion_payload)
    pol, sub, sl = detect_sentiment(el)
    
    db_add_diary_entry(user_id, message, el, pol)
    
    return {
        "reply": reply,
        "emotion": {"label": el.title(), "confidence": ec, "emoji": ee, "note": en},
        "sentiment": {"label": sl, "polarity": round(pol, 3), "subjectivity": round(sub, 3), "note": ""},
        "meta": {"muril_loaded": analyzer.weights_loaded}
    }

def api_health():
    return {"status": "ok", "muril_loaded": analyzer.weights_loaded}

# UI & Gradio mount
with gr.Blocks(title="MyHaven Mental Health AI") as demo:
    gr.Markdown("# 💛 MyHaven Mental Health Companion")
    gr.Markdown("MuRIL-BERT Emotion Classifier + Groq LLaMA-3.3-70B API Server is active.")
    
    with gr.Row():
        input_txt = gr.Textbox(label="Test Message", placeholder="Type how you are feeling...")
        out_txt = gr.JSON(label="Emotion & AI Response Output")
        
    btn = gr.Button("Analyze & Chat", variant="primary")
    btn.click(fn=lambda text: api_chat("web_user", text), inputs=input_txt, outputs=out_txt)

# Native Hugging Face Gradio launch (Hugging Face inspects `demo` directly)
if __name__ == "__main__":
    demo.launch()
