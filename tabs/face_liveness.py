"""Face Liveness Detection tab — POST /api/liveness."""

from __future__ import annotations

import base64
from pathlib import Path

import gradio as gr
import requests

from shared.backend import ROOT, env_url, missing_msg, product_links_md, IMAGE_SUFFIXES

SAMPLES = ROOT / "assets" / "examples" / "liveness"
API = env_url("FACE_LIVENESS_URL", "API_BASE")
MISSING = missing_msg("FACE_LIVENESS_URL")


def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _examples() -> list[str]:
    if not SAMPLES.is_dir():
        return []
    return sorted(
        str(p)
        for p in SAMPLES.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def check_image(path):
    if not API:
        return f"**Error:** {MISSING}"
    if not path:
        return "**Error:** Image required"
    try:
        r = requests.post(f"{API}/api/liveness", json={"image": _b64(path)}, timeout=180)
        payload = r.json()
    except Exception as ex:  # noqa: BLE001
        return f"**Error:** {ex}"
    if not isinstance(payload, dict) or not payload.get("success"):
        msg = payload.get("message") if isinstance(payload, dict) else payload
        return f"**Error:** {msg}"
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    result = data.get("result", "—")
    score = data.get("score", "—")
    passed = data.get("pass")
    pass_s = "true" if passed is True else "false" if passed is False else "—"
    return f"## {result}\n\n**Score:** {score}\n\n**Pass:** {pass_s}"


def mount(_demo: gr.Blocks) -> None:
    gr.Markdown(product_links_md("face_liveness"))
    if not API:
        gr.Markdown(MISSING)
    with gr.Row():
        with gr.Column():
            img = gr.Image(type="filepath", label="Face")
            examples = _examples()
            if examples:
                gr.Examples(examples, inputs=img, label="Examples")
            btn = gr.Button("Check Liveness", variant="primary")
        with gr.Column():
            summary = gr.Markdown(value="")
    btn.click(check_image, inputs=[img], outputs=[summary])
