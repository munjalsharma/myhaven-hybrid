# -*- coding: utf-8 -*-
"""
Hugging Face Spaces Entry Point for MyHaven.
Mounts the FastAPI app on the Free Gradio SDK (2 vCPU, 16 GB RAM).
Serves all REST API endpoints for the MyHaven Frontend seamlessly.
"""

import os
import gradio as gr
from main import app

# Mount FastAPI app directly onto Gradio
demo = gr.mount_gradio_app(app, gr.Blocks(title="MyHaven API Server"), path="/gradio")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
