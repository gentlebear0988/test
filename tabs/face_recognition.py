"""Face Recognition tab — Detect / Quality / Match."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any

import gradio as gr
import requests

from shared import demo_ui
from shared.backend import ROOT, env_url, missing_msg, product_links_md, IMAGE_SUFFIXES

SAMPLES = ROOT / "assets" / "examples" / "faces"
API = env_url("FACE_RECOGNITION_URL", "API_BASE")
MISSING = missing_msg("FACE_RECOGNITION_URL")


def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4g}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _list_images() -> list[Path]:
    if not SAMPLES.is_dir():
        return []
    return sorted(
        p for p in SAMPLES.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def _sample_index(path: Path) -> int | None:
    m = re.match(r"(?:odd|even)\((\d+)\)", path.stem, re.I)
    if m:
        return int(m.group(1))
    m = re.match(r"^(\d+)$", path.stem)
    if m:
        return int(m.group(1))
    return None


def _sorted_sample_paths() -> list[Path]:
    indexed = [(idx, p) for p in _list_images() if (idx := _sample_index(p)) is not None]
    indexed.sort(key=lambda item: item[0])
    return [p for _, p in indexed]


def _face_examples() -> list[str]:
    numbered = [str(p) for p in _sorted_sample_paths()]
    return numbered or [str(p) for p in _list_images()]


def _odd_examples() -> list[str]:
    return [str(p) for p in _sorted_sample_paths() if (_sample_index(p) or 0) % 2 == 1]


def _even_examples() -> list[str]:
    return [str(p) for p in _sorted_sample_paths() if (_sample_index(p) or 0) % 2 == 0]


def _error(msg: str):
    return f"**Error:** {msg}", [], ""


def _post(path: str, body: dict) -> dict | tuple:
    if not API:
        return _error(MISSING)
    try:
        r = requests.post(f"{API}{path}", json=body, timeout=120)
        payload = r.json()
    except Exception as ex:  # noqa: BLE001
        return _error(str(ex))
    if not isinstance(payload, dict):
        return "**Unexpected response.**", [], json.dumps(payload, indent=2)
    return payload


def _attr_value(attr: Any) -> str:
    if not isinstance(attr, dict):
        return _cell(attr)
    return _cell(attr.get("value"))


def _attr_extra(attr: Any, *, kind: str) -> str:
    if not isinstance(attr, dict):
        return ""
    if kind == "detect":
        if "confidence" in attr:
            return _cell(attr["confidence"])
        return ""
    parts = []
    if "status" in attr:
        parts.append(f"status={_cell(attr['status'])}")
    if "range" in attr:
        parts.append(f"range={_cell(attr['range'])}")
    return ", ".join(parts)


def format_detect(payload: dict) -> tuple[str, list[list[str]], str]:
    status = payload.get("status")
    faces = payload.get("data") if isinstance(payload.get("data"), list) else []
    summary = (
        f"**Detect** — status={status}  ·  faces={len(faces)}"
        + (f"  ·  {payload.get('message')}" if payload.get("message") else "")
    )
    rows: list[list[str]] = []
    for face in faces:
        if not isinstance(face, dict):
            continue
        face_id = face.get("faceId", "")
        prefix = f"face[{face_id}]"
        rows.append([f"{prefix}.facePose", _cell(face.get("facePose")), ""])
        rows.append([f"{prefix}.faceRegion", _cell(face.get("faceRegion")), ""])
        attrs = face.get("attributes") or {}
        if isinstance(attrs, dict):
            for name, attr in attrs.items():
                rows.append(
                    [f"{prefix}.{name}", _attr_value(attr), _attr_extra(attr, kind="detect")]
                )
    raw = json.dumps(payload, indent=2, ensure_ascii=False)
    return summary, rows, raw


def format_quality(payload: dict) -> tuple[str, list[list[str]], str]:
    status = payload.get("status")
    faces = payload.get("data") if isinstance(payload.get("data"), list) else []
    summary = (
        f"**Quality** — status={status}  ·  faces={len(faces)}"
        + (f"  ·  {payload.get('message')}" if payload.get("message") else "")
    )
    rows: list[list[str]] = []
    for face in faces:
        if not isinstance(face, dict):
            continue
        face_id = face.get("faceId", "")
        prefix = f"face[{face_id}]"
        attrs = face.get("attributes") or {}
        if isinstance(attrs, dict):
            for name, attr in attrs.items():
                rows.append(
                    [f"{prefix}.{name}", _attr_value(attr), _attr_extra(attr, kind="quality")]
                )
    raw = json.dumps(payload, indent=2, ensure_ascii=False)
    return summary, rows, raw


def format_match(payload: dict) -> tuple[str, list[list[str]], str]:
    status = payload.get("status")
    matches = payload.get("match") if isinstance(payload.get("match"), list) else []
    summary = (
        f"**Match** — status={status}  ·  pairs={len(matches)}"
        + (f"  ·  {payload.get('message')}" if payload.get("message") else "")
    )
    rows: list[list[str]] = []
    for i, item in enumerate(matches):
        if not isinstance(item, dict):
            continue
        label = (
            f"img{item.get('firstImageId')}#face{item.get('firstFaceId')}"
            f" ↔ img{item.get('secondImageId')}#face{item.get('secondFaceId')}"
        )
        rows.append([f"pair[{i}]", label, _cell(item.get("similarity"))])
    if not rows and status == 0:
        rows.append(["similarity", "—", "no face pair"])
    raw = json.dumps(payload, indent=2, ensure_ascii=False)
    return summary, rows, raw


def detect(image):
    if not image:
        return _error("Image required")
    out = _post("/api/detect", {"image": _b64(image), "cropImage": False})
    if isinstance(out, tuple):
        return out
    return format_detect(out)


def quality(image):
    if not image:
        return _error("Image required")
    out = _post("/api/quality", {"image": _b64(image), "cropImage": False})
    if isinstance(out, tuple):
        return out
    return format_quality(out)


def match(image1, image2):
    if not image1 or not image2:
        return _error("Both images required")
    out = _post(
        "/api/match",
        {"image1": _b64(image1), "image2": _b64(image2), "cropImage": False},
    )
    if isinstance(out, tuple):
        return out
    return format_match(out)


def _result_panel(*, headers: list[str], label: str):
    with gr.Tabs():
        with gr.Tab("Result"):
            summary = gr.Markdown(value="*Run an action to see fields.*")
            table = demo_ui.result_dataframe(headers=headers, label=label)
        with gr.Tab("Raw JSON"):
            raw = gr.Code(language="json", label="API response")
    return summary, table, raw


def mount(_demo: gr.Blocks) -> None:
    detect_ex = _face_examples()
    odd_ex = _odd_examples()
    even_ex = _even_examples()

    gr.Markdown(product_links_md("face_recognition"))
    if not API:
        gr.Markdown(MISSING)

    with gr.Tabs():
        with gr.Tab("Detect"):
            with gr.Row():
                with gr.Column():
                    det_in = gr.Image(type="filepath", label="Face")
                    if detect_ex:
                        gr.Examples(detect_ex, inputs=det_in, label="Examples")
                    det_btn = gr.Button("Detect", variant="primary")
                with gr.Column():
                    det_summary, det_table, det_raw = _result_panel(
                        headers=["Attribute", "Value", "Confidence"],
                        label="Detect attributes",
                    )
            det_btn.click(detect, inputs=det_in, outputs=[det_summary, det_table, det_raw])

        with gr.Tab("Quality"):
            with gr.Row():
                with gr.Column():
                    q_in = gr.Image(type="filepath", label="Face")
                    if detect_ex:
                        gr.Examples(detect_ex, inputs=q_in, label="Examples")
                    q_btn = gr.Button("Quality", variant="primary")
                with gr.Column():
                    q_summary, q_table, q_raw = _result_panel(
                        headers=["Check", "Value", "Status / range"],
                        label="Quality checks",
                    )
            q_btn.click(quality, inputs=q_in, outputs=[q_summary, q_table, q_raw])

        with gr.Tab("Match"):
            gr.Markdown("Pick **one Odd** image and **one Even** image, then click Match.")
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        m1 = gr.Image(type="filepath", label="Odd")
                        m2 = gr.Image(type="filepath", label="Even")
                    with gr.Row():
                        if odd_ex:
                            gr.Examples(odd_ex, inputs=m1, label="Odd")
                        if even_ex:
                            gr.Examples(even_ex, inputs=m2, label="Even")
                    match_btn = gr.Button("Match", variant="primary")
                with gr.Column():
                    m_summary, m_table, m_raw = _result_panel(
                        headers=["Pair", "Faces", "Similarity"],
                        label="Match scores",
                    )
            match_btn.click(match, inputs=[m1, m2], outputs=[m_summary, m_table, m_raw])
