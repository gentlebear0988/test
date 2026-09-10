"""ID Document Recognition tab — POST /api/documentRecognition."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import gradio as gr
import requests

from shared import ui
from shared.backend import ROOT, env_url, missing_msg, product_links_md, IMAGE_SUFFIXES
from shared.images_view import gallery_from_payload
from shared.result_view import build_result_view

SAMPLES = ROOT / "assets" / "examples" / "documents"
API = env_url("DOCUMENT_READER_URL", "DOCUMENT_RECOGNITION_URL", "API_BASE")
MISSING = missing_msg("DOCUMENT_READER_URL")


def _fetch_license_status() -> dict:
    if not API:
        return {}
    try:
        r = requests.get(f"{API}/api/licenseStatus", timeout=5)
        body = r.json() if r.ok else {}
        data = body.get("data") if isinstance(body, dict) else None
        return data if isinstance(data, dict) else {}
    except Exception:  # noqa: BLE001
        return {}


def _license_banner_md(status: dict | None = None) -> str:
    if not API:
        return MISSING
    st = status if status is not None else _fetch_license_status()
    label = str(st.get("label") or "").strip()
    if not label:
        if st.get("licensed"):
            label = str(st.get("levelName") or "Licensed")
        else:
            label = "Not licensed / unavailable"
    return f"**License:** {label}"


def _capability_notes(status: dict) -> list[str]:
    notes: list[str] = []
    if not status.get("recognition"):
        notes.append(
            "Recognition (OCR / MRZ / Barcode) is **not available** on this license."
        )
    return notes


def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _list_images() -> list[Path]:
    if not SAMPLES.is_dir():
        return []
    return sorted(
        p for p in SAMPLES.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def _document_examples() -> list[list[str | None]]:
    files = {p.name: p for p in _list_images()}
    pairs: list[list[str | None]] = []
    used: set[str] = set()
    for path in sorted(files.values()):
        if "_front" not in path.stem:
            continue
        base = path.stem.rsplit("_front", 1)[0]
        back = None
        for suf in IMAGE_SUFFIXES:
            cand = files.get(f"{base}_back{suf}")
            if cand:
                back = cand
                break
        pairs.append(
            [
                str(path.resolve()),
                str(back.resolve()) if back else None,
            ]
        )
        used.add(path.name)
        if back:
            used.add(back.name)
    for path in _list_images():
        if path.name not in used:
            pairs.append([str(path.resolve()), None])
    return pairs


def document_recognition(front, back):
    empty: list[list[str]] = []
    none_gallery: list = []
    if not API:
        err = f"**Error:** {MISSING}"
        return (err, empty, none_gallery, "")

    lic = _fetch_license_status()
    notes = _capability_notes(lic)
    if not front:
        err = "**Error:** Front image required."
        if notes:
            err = "\n\n".join(f"**Note:** {n}" for n in notes) + "\n\n" + err
        return (err, empty, none_gallery, "")

    if notes and not lic.get("recognition"):
        msg = "\n\n".join(f"**Note:** {n}" for n in notes)
        return (msg, empty, none_gallery, "")

    images = [{"image": _b64(front), "page_idx": 0}]
    if back:
        images.append({"image": _b64(back), "page_idx": 1})

    try:
        r = requests.post(
            f"{API}/api/documentRecognition",
            json={"images": images},
            timeout=180,
        )
    except Exception as ex:  # noqa: BLE001
        return (f"**Request failed:** {ex}", empty, none_gallery, "")

    try:
        payload = r.json()
    except Exception:  # noqa: BLE001
        return (
            f"**Invalid JSON** (HTTP {r.status_code})",
            empty,
            none_gallery,
            r.text or "",
        )

    if not isinstance(payload, dict):
        return (
            "**Unexpected response shape.**",
            empty,
            none_gallery,
            json.dumps(payload, indent=2),
        )

    summary, rows = build_result_view(payload)
    prefix: list[str] = []
    for n in notes:
        prefix.append(f"**Note:** {n}")
    lic_err = str(payload.get("licenseError") or "").strip()
    if lic_err:
        prefix.append(f"**License:** {lic_err}")
    if prefix:
        summary = "\n\n".join(prefix) + "\n\n" + summary
    gallery = gallery_from_payload(payload)
    if not gallery:
        summary += "\n\n*No cropped images in this response (Images tab empty).*"
    return (summary, rows, gallery, json.dumps(payload, indent=2))


def mount(demo: gr.Blocks) -> None:
    examples = _document_examples()
    gr.Markdown(product_links_md("document_recognition"))
    license_md = gr.Markdown(value=_license_banner_md())
    with gr.Row():
        with gr.Column():
            front = gr.Image(type="filepath", label="Front")
            back = gr.Image(type="filepath", label="Back")
            if examples:
                gr.Examples(
                    examples=examples,
                    inputs=[front, back],
                    label="Examples",
                    examples_per_page=8,
                )
            btn = gr.Button("ID Card Recognition", variant="primary")
        with gr.Column():
            with gr.Tabs():
                with gr.Tab("Result"):
                    summary = gr.Markdown(value="")
                    table = ui.result_dataframe()
                with gr.Tab("Images"):
                    gallery = ui.result_gallery(
                        label="Portrait / signature / cropped pages"
                    )
                with gr.Tab("Raw JSON"):
                    raw = gr.Code(language="json", label="API response")
    btn.click(
        document_recognition,
        inputs=[front, back],
        outputs=[summary, table, gallery, raw],
    )
    btn.click(lambda: _license_banner_md(), outputs=[license_md])
    demo.load(lambda: _license_banner_md(), outputs=[license_md])
