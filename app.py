"""FacePlugin Playground — four-tab Gradio demo (HTTP clients only)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import shared.backend  # noqa: F401 — load .env before tab modules read URLs
import gradio as gr

from shared.demo_ui import RESULT_CSS as FACE_CSS
from shared.ui import RESULT_CSS as DOC_CSS
from tabs.document_liveness import mount as mount_document_liveness
from tabs.document_recognition import mount as mount_document_recognition
from tabs.face_liveness import mount as mount_face_liveness
from tabs.face_recognition import mount as mount_face_recognition

HEADER_MD = """
# FacePlugin Online Demo
We provide a range of SDKs, including face liveness detection, face recognition, ID document recognition, ID document liveness detection, and more.
"""

with gr.Blocks(title="FacePlugin Online Demo") as demo:
    gr.Markdown(HEADER_MD)
    with gr.Tabs():
        with gr.Tab("Face Liveness Detection"):
            mount_face_liveness(demo)
        with gr.Tab("Face Recognition"):
            mount_face_recognition(demo)
        with gr.Tab("ID Card Recognition"):
            mount_document_recognition(demo)
        with gr.Tab("ID Document Liveness Detection"):
            mount_document_liveness(demo)

if __name__ == "__main__":
    demo.queue().launch(css=DOC_CSS + FACE_CSS)
