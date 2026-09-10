<div align="center">
<img alt="FacePlugin" src="https://avatars.githubusercontent.com/u/160751046?s=200&v=4" width="200"/>
</div>

#### 🌐 Company Site - [Here](https://faceplugin.com)
#### 🤗 Hugging Face - [Here](https://huggingface.co/FacePlugin-Ltd)
#### 🛟 Help Center - [Here](https://doc.faceplugin.com)
#### 🐳 Docker Hub - [Here](https://hub.docker.com/u/faceplugin)

# FacePlugin Playground

Gradio demo UI for four FacePlugin Linux / Docker APIs, laid out like [web.kby-ai.com](https://web.kby-ai.com/). This folder is **UI only** — no `lib/cpu`, no Flask server. Each tab POSTs images to the matching backend URL from `.env`. Backend URLs are never shown in the Gradio UI.

| Tab | GitHub (Linux / Docker) | Docker Hub | API |
| --- | ----------------------- | ---------- | --- |
| Face Liveness Detection | [FaceLivenessDetection-Docker](https://github.com/Faceplugin-ltd/FaceLivenessDetection-Docker) | [faceplugin/face-liveness](https://hub.docker.com/r/faceplugin/face-liveness) | `POST /api/liveness` |
| Face Recognition | [FaceRecognition-Docker](https://github.com/Faceplugin-ltd/FaceRecognition-Docker) | [faceplugin/face-recognition](https://hub.docker.com/r/faceplugin/face-recognition) | `POST /api/detect` · `/api/quality` · `/api/match` |
| ID Card Recognition | [ID-Document-Recognition-Docker](https://github.com/Faceplugin-ltd/ID-Document-Recognition-Docker) | [faceplugin/document-reader](https://hub.docker.com/r/faceplugin/document-reader) | `POST /api/documentRecognition` |
| ID Document Liveness Detection | [ID-Document-Liveness-Detection-Docker](https://github.com/Faceplugin-ltd/ID-Document-Liveness-Detection-Docker) | [faceplugin/document-liveness](https://hub.docker.com/r/faceplugin/document-liveness) | `POST /api/documentLiveness` |

Face Recognition has inner tabs **Detect**, **Quality**, and **Match**.

## Run locally

```bash
cd platform/playground
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set the four *_URL values to your running APIs (no trailing slash)
python app.py
```

If a tab’s URL is unset, that tab shows a generic unavailable message and does not call `127.0.0.1`.

## Contact

<div align="left">
<a target="_blank" href="mailto:info@faceplugin.com"><img src="https://img.shields.io/badge/email-info@faceplugin.com-blue.svg?logo=gmail" alt="faceplugin.com"></a>&emsp;
<a target="_blank" href="https://wa.me/+14692784822"><img src="https://img.shields.io/badge/whatsapp-faceplugin-blue.svg?logo=whatsapp" alt="faceplugin.com"></a>
</div>
