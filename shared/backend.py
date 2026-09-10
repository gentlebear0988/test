"""Playground root and per-tab API base URLs (never default to localhost)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

SERVICE_UNAVAILABLE = "This demo is temporarily unavailable. Please try again later."

# GitHub Docker repo + Docker Hub for each playground tab.
PRODUCT_LINKS = {
    "document_recognition": {
        "github": "https://github.com/Faceplugin-ltd/ID-Document-Recognition-Docker",
        "docker": "https://hub.docker.com/r/faceplugin/document-reader",
    },
    "document_liveness": {
        "github": "https://github.com/Faceplugin-ltd/ID-Document-Liveness-Detection-Docker",
        "docker": "https://hub.docker.com/r/faceplugin/document-liveness",
    },
    "face_liveness": {
        "github": "https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker",
        "docker": "https://hub.docker.com/r/faceplugin/face-liveness",
    },
    "face_recognition": {
        "github": "https://github.com/Faceplugin-ltd/FaceRecognition-Docker",
        "docker": "https://hub.docker.com/r/faceplugin/face-recognition",
    },
}


def env_url(*keys: str) -> str:
    for key in keys:
        value = (os.getenv(key) or "").strip().rstrip("/")
        if value:
            return value
    return ""


def missing_msg(_var: str = "") -> str:
    return SERVICE_UNAVAILABLE


def docker_hub_md(key: str) -> str:
    return f"##### Docker Hub - {PRODUCT_LINKS[key]['docker']}"


def product_links_md(key: str) -> str:
    return docker_hub_md(key)
